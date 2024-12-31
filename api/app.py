from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import Settings
from api.db import Database
from api.endpoints.appointments import AppointmentsAPI
from api.endpoints.payment import PaymentAPI
from api.kv import KiwiStore
from api.slots import FreshDayBreaker, SlotsLoader
from api.tasks.emails import EmailTask


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings()
    db = Database(database_url=settings.database_url)
    kv = KiwiStore(db)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        del app
        db.create_tables()
        yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "null",
            "http://localhost",
            "http://127.0.0.1",
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "https://seattle-beauty-lounge.com",
            "https://static.staging.seattle-beauty-lounge.com",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    AppointmentsAPI(
        db,
        email_task=EmailTask(settings),
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
