from fastapi import BackgroundTasks, FastAPI

from api.db import Database
from api.models import Appointment, AppointmentCreate
from api.slots import SlotsLoader
from api.tasks.calendar import CalendarTaskDummy
from api.tasks.emails import EmailTaskDummy


class AppointmentsAPI:
    def __init__(
        self,
        db: Database,
        email_task: EmailTaskDummy,
        calendar_task: CalendarTaskDummy,
        slots_loader: SlotsLoader,
    ) -> None:
        self._db = db
        self._email_task = email_task
        self._calendar_task = calendar_task
        self._slots_loader = slots_loader

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
        background_tasks.add_task(
            self._email_task.send_confirmation_email,
            appointment,
        )
        background_tasks.add_task(
            self._calendar_task.create_event,
            appointment,
        )
        return appointment

    def get_availability(self):
        return self._slots_loader.gen_ranges()

    def register(self, app: FastAPI, prefix: str = "") -> None:
        app.add_api_route(
            prefix + "/appointments",
            self.create_appointment,
            response_model=Appointment,
            methods=["POST"],
        )
        app.add_api_route(
            prefix + "/availability",
            self.get_availability,
            methods=["GET"],
        )
