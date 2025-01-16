from fastapi import FastAPI
from sqlmodel import select

from api.db import Database
from api.models import Appointment
from api.services import ServicesInfo

app = FastAPI()


class BackofficeAPI:
    def __init__(self, db: Database, services: ServicesInfo) -> None:
        self._db = db
        self._services = services

    def appointment(self, id: int) -> Appointment | None:
        with self._db.session() as session:
            appointment = session.exec(
                select(Appointment).where(
                    Appointment.id == id,
                )
            ).first()
        return {"appointment": self.serialize_appointment(appointment)}

    def serialize_appointment(self, appointment: Appointment) -> dict:
        return {c.name: getattr(appointment, c.name) for c in Appointment.__table__.columns}

    def register(self, app_: FastAPI, prefix: str = "") -> None:
        app_.add_api_route(
            prefix + "/appointment/{id}",
            self.appointment,
            methods=["GET"],
            response_model=Appointment,
        )
