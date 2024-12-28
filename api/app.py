from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import Settings
from api.db import Database
from api.endpoints.appointments import AppointmentsAPI
from api.endpoints.payment import PaymentAPI
from api.tasks.emails import EmailTask


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings()
    db = Database(database_url=settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
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
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    AppointmentsAPI(db, email_task=EmailTask(settings)).register(app)
    PaymentAPI("http://localhost:5173/return", settings.strip_api_key).register(app)
    if settings.proxy_frontend:
        app.mount("/", StaticFiles(directory="public"), name="static")
    return app
