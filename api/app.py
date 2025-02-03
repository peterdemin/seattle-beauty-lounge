from contextlib import asynccontextmanager
from typing import Optional

import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.calendar_client import (
    CalendarEventParser,
    CalendarService,
    CalendarServiceDummy,
    DayBreaker,
)
from api.config import Settings
from api.db import Database
from api.endpoints.appointments import AppointmentsAPI
from api.endpoints.backoffice import BackofficeAPI
from api.endpoints.square_payment import SquarePaymentAPI
from api.google_auth import GoogleAuth
from api.kv import KiwiStore
from api.service_catalog import ServiceCatalog
from api.slots import FreshDayBreaker, SlotsLoader
from api.sms_client import SMSClient
from api.smtp_client import SMTPClient, SMTPClientDummy
from api.square_client import SquareClient
from api.task_scheduler import TaskScheduler
from api.tasks.availability import AvailabilityTask
from api.tasks.calendar import CalendarTask
from api.tasks.emails import EmailTask
from api.tasks.reminder import ReminderTask


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings()

    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=1.0,
            _experiments={
                "continuous_profiling_auto_start": True,
            },
        )

    db = Database(database_url=settings.database_url)
    kv = KiwiStore(db)
    task_scheduler = TaskScheduler()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        del app
        task_scheduler.start()
        db.create_tables()
        yield
        task_scheduler.stop()

    service_catalog = ServiceCatalog()
    calendar_service = (
        CalendarService(GoogleAuth.delegated(settings.sender_email))
        if settings.enable_calendar
        else CalendarServiceDummy()
    )
    if settings.enable_calendar:
        AvailabilityTask(
            key="busy_dates",
            kv=kv,
            calendar_service=calendar_service,
            calendar_event_parser=CalendarEventParser(),
            day_breaker=DayBreaker({}),
        ).register(task_scheduler)
    calendar_task = CalendarTask(
        calendar_service=calendar_service,
        service_catalog=service_catalog,
    )
    if settings.twilio_account_sid:
        ReminderTask(
            sms_client=SMSClient(
                account_sid=settings.twilio_account_sid,
                auth_token=settings.twilio_auth_token,
                from_number=settings.twilio_from_number,
            ),
            db=db,
            service_catalog=service_catalog,
        ).register(task_scheduler)

    email_task = EmailTask(
        smtp_client=(
            SMTPClient(sender_email=settings.sender_email, sender_password=settings.sender_password)
            if settings.enable_emails
            else SMTPClientDummy()
        ),
        service_catalog=service_catalog,
    )

    app = FastAPI(lifespan=lifespan)
    AppointmentsAPI(
        db,
        email_task=email_task,
        calendar_task=calendar_task,
        slots_loader=SlotsLoader.load(
            day_breaker=FreshDayBreaker(kv),
        ),
    ).register(app, prefix=settings.location_prefix)
    if settings.enable_admin:
        BackofficeAPI(
            db,
            service_catalog,
        ).register(app, prefix="/admin" + settings.location_prefix)
    SquarePaymentAPI(
        square_client=SquareClient(
            access_token=settings.square_access_token,
            square_environment=settings.square_environment,
            square_location_id=settings.square_location_id,
            application_id=settings.square_application_id,
        )
    ).register(app, prefix=settings.location_prefix + "/square")

    if settings.proxy_frontend:
        app.mount("/", StaticFiles(directory="public"), name="static")
    return app
