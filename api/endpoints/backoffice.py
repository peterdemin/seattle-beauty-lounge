import dataclasses

from fastapi import FastAPI
from sqlmodel import Session, select

from api.db import Database
from api.models import Appointment
from api.service_catalog import ServiceCatalog

app = FastAPI()


class BackofficeAPI:
    def __init__(self, db: Database, service_catalog: ServiceCatalog) -> None:
        self._db = db
        self._service_catalog = service_catalog

    def appointment(self, id: int) -> dict[str, dict | list[dict]]:
        with self._db.session() as session:
            appointment = session.exec(
                select(Appointment).where(
                    Appointment.id == id,
                )
            ).first()
            if not appointment:
                return {}
            appointment_data = self.serialize_appointment(appointment)
            return {
                "appointment": appointment_data,
                "more": [
                    self.serialize_appointment(a)
                    for a in self.get_other_appointments(session, appointment)
                ],
            }

    def get_other_appointments(
        self, session: Session, appointment: Appointment
    ) -> list[Appointment]:
        return list(
            session.exec(
                select(Appointment)
                .where(
                    (
                        (Appointment.clientPhone == appointment.clientPhone)
                        | (Appointment.clientEmail == appointment.clientEmail)
                    )
                    & (Appointment.id != appointment.id)
                )
                .order_by(Appointment.date, Appointment.time)
            ).all()
        )

    def serialize_appointment(self, appointment: Appointment) -> dict:
        result = {c.name: getattr(appointment, c.name) for c in Appointment.__table__.columns}
        try:
            service_info = self._service_catalog.get_service(appointment.serviceId)
        except KeyError:
            pass
        else:
            result["service"] = dataclasses.asdict(service_info)
        return result

    def register(self, app_: FastAPI, prefix: str = "") -> None:
        app_.add_api_route(
            prefix + "/appointment/{id}",
            self.appointment,
            methods=["GET"],
        )
