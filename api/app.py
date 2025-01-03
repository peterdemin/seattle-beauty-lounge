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
from api.endpoints.payment import PaymentAPI
from api.google_auth import GoogleAuth
from api.kv import KiwiStore
from api.services import ServicesInfo
from api.slots import FreshDayBreaker, SlotsLoader
from api.smtp_client import SMTPClient, SMTPClientDummy
from api.task_scheduler import TaskScheduler
from api.tasks.availability import AvailabilityTask
from api.tasks.calendar import CalendarTask
from api.tasks.emails import EmailTask


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

    services_info = ServicesInfo.load()
    calendar_service = (
        CalendarService(GoogleAuth.delegated(settings.sender_email))
        if settings.enable_calendar
        else CalendarServiceDummy()
    )
    if settings.enable_calendar:
        availability_task = AvailabilityTask(
            key="busy_dates",
            kv=kv,
            calendar_service=calendar_service,
            calendar_event_parser=CalendarEventParser(),
            day_breaker=DayBreaker({}),
        )
        task_scheduler.every().minute.do(availability_task)
    calendar_task = CalendarTask(
        calendar_service=calendar_service,
        services_info=services_info,
    )

    smtp_client: SMTPClientDummy = (
        SMTPClient(sender_email=settings.sender_email, sender_password=settings.sender_password)
        if settings.enable_emails
        else SMTPClientDummy()
    )
    email_task = EmailTask(
        smtp_client=smtp_client,
        services_info=services_info,
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
    PaymentAPI(
        "https://seattle-beauty-lounge.com",
        settings.stripe_api_key,
    ).register(app, prefix=settings.location_prefix)

    if settings.proxy_frontend:
        app.mount("/", StaticFiles(directory="public"), name="static")
    return app
