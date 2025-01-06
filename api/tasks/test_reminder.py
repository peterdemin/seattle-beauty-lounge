import datetime
from unittest import mock

from sqlmodel import select

from api.constants import TIMEZONE
from api.db import Database
from api.models import Appointment
from api.sms_client import SMSClientDummy
from api.tasks.reminder import ReminderTask


def test_reminder_task_happy_path() -> None:
    db = Database("sqlite://")
    db.create_tables()
    sms_client = mock.Mock(spec=SMSClientDummy)
    with db.session() as session:
        session.add(
            Appointment(
                serviceId="service",
                date=datetime.date(2014, 4, 14),
                time=datetime.time(10, 11),
                clientName="clientName",
                clientPhone="2403421438",
                clientEmail="clientEmail",
            )
        )
        session.commit()
    reminder = ReminderTask(sms_client=sms_client, db=db)
    job_time = TIMEZONE.localize(datetime.datetime(2014, 4, 13, 14, 0))
    reminder(job_time)
    sms_client.send.assert_called_once_with(
        "2403421438",
        "clientName, you have service scheduled for tomorrow, Monday, April 14 at 10:11.",
    )
    with db.session() as session:
        appointments = session.exec(select(Appointment)).all()
    assert len(appointments) == 1
    assert appointments[0].remindedAt > 0


def test_reminder_task_skips_at_night() -> None:
    db = mock.Mock(spec=Database)
    sms_client = SMSClientDummy()
    reminder = ReminderTask(sms_client=sms_client, db=db)
    job_time = TIMEZONE.localize(datetime.datetime(2014, 4, 13, 2, 0))
    reminder(job_time)
    db.session.assert_not_called()
