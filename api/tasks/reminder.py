import datetime
import time
from typing import Optional

from sqlmodel import select

from api.constants import TIMEZONE
from api.db import Database
from api.models import Appointment
from api.sms_client import SMSClientDummy
from api.task_scheduler import TaskScheduler


class ReminderTask:
    _BATCH_LIMIT = 10
    _MESSAGE_TEMPLATE = (
        "{appointment.clientName}, you have {appointment.serviceId} scheduled "
        "for tomorrow, {date_str} at {time_str}."
    )
    _ACTIVE_HOURS = (9, 18)

    def __init__(
        self,
        sms_client: SMSClientDummy,
        db: Database,
    ) -> None:
        self._sms_client = sms_client
        self._db = db

    def __call__(self, job_time: Optional[datetime.datetime] = None) -> None:
        job_time = job_time or TIMEZONE.localize(datetime.datetime.now(tz=datetime.timezone.utc))
        if not self._should_run(job_time):
            return
        tomorrow = job_time.date() + datetime.timedelta(days=1)
        with self._db.session() as session:
            appointments = session.exec(
                select(Appointment)
                .where(
                    Appointment.date == tomorrow,
                    Appointment.remindedAt == 0,
                )
                .limit(self._BATCH_LIMIT)
            ).all()
        for appointment in appointments:
            self._send_reminder(appointment)
            with self._db.session() as session:
                appointment.remindedAt = int(time.time())
                session.add(appointment)
                session.commit()

    def register(self, task_scheduler: TaskScheduler) -> None:
        task_scheduler.every().hour.do(self)

    def _should_run(self, job_time: datetime.datetime) -> bool:
        return self._ACTIVE_HOURS[0] < job_time.hour < self._ACTIVE_HOURS[1]

    def _send_reminder(self, appointment: Appointment) -> None:
        self._sms_client.send(
            appointment.clientPhone,
            self._MESSAGE_TEMPLATE.format(
                appointment=appointment,
                date_str=appointment.date.strftime("%A, %B %d"),
                time_str=appointment.time.strftime("%H:%M"),
            ),
        )
