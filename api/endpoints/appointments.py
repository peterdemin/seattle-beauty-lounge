from fastapi import BackgroundTasks, FastAPI

from api.db import Database
from api.models import Appointment, AppointmentCreate
from api.tasks.emails import send_confirmation_email


class AppointmentsAPI:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create_appointment(
        self,
        appointment_data: AppointmentCreate,
        background_tasks: BackgroundTasks,
    ):
        """Creates a new appointment.

        - Stores it in the DB,
        - Starts a background task to send a confirmation email.
        """
        appointment = Appointment.model_validate(appointment_data)
        with self._db.session() as session:
            session.add(appointment)
            session.commit()
            session.refresh(appointment)
        background_tasks.add_task(send_confirmation_email, appointment)
        return appointment

    def register(self, app_: FastAPI, prefix: str = "") -> None:
        app_.add_api_route(
            prefix + "/appointments",
            self.create_appointment,
            response_model=Appointment,
            methods=["POST"],
        )
