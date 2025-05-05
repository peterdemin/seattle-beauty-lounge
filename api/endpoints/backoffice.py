import dataclasses
import subprocess

from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from api.db import Database
from api.models import Appointment
from api.service_catalog import ServiceCatalog

app = FastAPI()


class BackofficeAPI:
    def __init__(self, db: Database, service_catalog: ServiceCatalog) -> None:
        self._db = db
        self._service_catalog = service_catalog

    def register(self, app_: FastAPI, prefix: str = "", enable_build: bool = False) -> None:
        app_.add_api_route(
            prefix + "/appointment/{id}",
            self.appointment,
            methods=["GET"],
        )
        if enable_build:
            app_.add_api_route(
                prefix + "/build",
                self.build,
                methods=["POST"],
            )

    def appointment(self, app_id: int) -> dict[str, dict | list[dict]]:
        with self._db.session() as session:
            appointment = session.exec(
                select(Appointment).where(
                    Appointment.id == app_id,
                )
            ).first()
            if not appointment:
                return {}
            appointment_data = self._serialize_appointment(appointment)
            return {
                "appointment": appointment_data,
                "more": [
                    self._serialize_appointment(a)
                    for a in self._get_other_appointments(session, appointment)
                ],
            }

    def build(self, request: Request) -> RedirectResponse:
        subprocess.run(["make", "content", "fe"], check=True)
        return RedirectResponse(
            url=request.headers.get("referer") or "/",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    def _get_other_appointments(
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

    def _serialize_appointment(self, appointment: Appointment) -> dict:
        result = {c.name: getattr(appointment, c.name) for c in Appointment.__table__.columns}
        try:
            service_info = self._service_catalog.get_service(appointment.serviceId)
        except KeyError:
            pass
        else:
            result["service"] = dataclasses.asdict(service_info)
        return result
