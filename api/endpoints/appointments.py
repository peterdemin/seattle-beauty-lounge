from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse

from api.db import Database
from api.models import Appointment, AppointmentCreate
from api.slots import SlotsLoader
from api.square_client import CreatePaymentResult, SquareClientDummy
from api.tasks.calendar import CalendarTask
from api.tasks.emails import EmailTask


class AppointmentsAPI:
    def __init__(
        self,
        *,
        db: Database,
        email_task: EmailTask,
        calendar_task: CalendarTask,
        slots_loader: SlotsLoader,
        square_client: SquareClientDummy,
    ) -> None:
        self._db = db
        self._email_task = email_task
        self._calendar_task = calendar_task
        self._slots_loader = slots_loader
        self._square_client = square_client

    def create_appointment(
        self,
        appointment_data: AppointmentCreate,
        background_tasks: BackgroundTasks,
    ) -> JSONResponse | Appointment:
        """Creates a new appointment.

        - Stores it in the DB,
        - Starts a background task to send a confirmation email.
        """
        appointment = Appointment.model_validate(appointment_data)
        with self._db.session() as session:
            session.add(appointment)
            session.commit()
            session.refresh(appointment)
        receipt: CreatePaymentResult = self._square_client.create_payment(appointment_data.payment)
        if receipt.get("error"):
            return JSONResponse(status_code=422, content=receipt)
        appointment.depositToken = receipt.get("id", "Empty payment ID")
        with self._db.session() as session:
            session.add(appointment)
            session.commit()
            session.refresh(appointment)
        background_tasks.add_task(
            self._email_task.on_appointment,
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
            methods=["POST"],
            response_model=None,
        )
        app.add_api_route(
            prefix + "/availability",
            self.get_availability,
            methods=["GET"],
        )
