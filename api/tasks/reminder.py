import contextlib
import datetime
import time
from typing import Optional

from sqlmodel import select
from tenacity import retry, stop_after_delay, wait_fixed

from api.constants import TIMEZONE
from api.db import Database
from api.models import Appointment
from api.service_catalog import ServiceCatalog
from api.sms_client import SMSClientDummy
from api.task_scheduler import TaskScheduler


class ReminderTask:
    _BATCH_LIMIT = 10
    _MESSAGE_TEMPLATE = (
        "{appointment.clientName}, you have {title} scheduled "
        "for tomorrow, {date_str} at {time_str}."
    )
    _ACTIVE_HOURS = (9, 18)

    def __init__(
        self,
        sms_client: SMSClientDummy,
        db: Database,
        service_catalog: ServiceCatalog,
    ) -> None:
        self._sms_client = sms_client
        self._db = db
        self._service_catalog = service_catalog

    def __call__(self, job_time: Optional[datetime.datetime] = None) -> None:
        job_time = job_time or datetime.datetime.now(tz=datetime.timezone.utc).astimezone(TIMEZONE)
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
        with contextlib.suppress(Exception):
            self._send(
                appointment.clientPhone,
                self._MESSAGE_TEMPLATE.format(
                    appointment=appointment,
                    title=self._service_catalog.get_title(appointment.serviceId),
                    date_str=appointment.date.strftime("%A, %B %d"),
                    time_str=appointment.time.strftime("%H:%M"),
                ),
            )

    @retry(stop=stop_after_delay(60), wait=wait_fixed(10))
    def _send(self, phone_number: str, message: str) -> None:
        self._sms_client.send(phone_number, message)
