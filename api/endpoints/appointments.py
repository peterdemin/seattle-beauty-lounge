import uuid

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import select

from api.db import Database
from api.linker import Linker
from api.models import Appointment, AppointmentCreate, AppointmentFull
from api.service_catalog import ServiceCatalog
from api.slots import SlotsLoader
from api.square_client import CreatePaymentResult, SquareClientDummy
from api.tasks.calendar import CalendarTask
from api.tasks.emails import EmailTask


class AppointmentsAPI:
    def __init__(
        self,
        *,
        linker: Linker,
        db: Database,
        email_task: EmailTask,
        calendar_task: CalendarTask,
        slots_loader: SlotsLoader,
        square_client: SquareClientDummy,
        service_catalog: ServiceCatalog,
    ) -> None:
        # pylint: disable=too-many-arguments
        self._linker = linker
        self._db = db
        self._email_task = email_task
        self._calendar_task = calendar_task
        self._slots_loader = slots_loader
        self._square_client = square_client
        self._service_catalog = service_catalog

    def create_appointment(
        self,
        appointment_data: AppointmentCreate,
        background_tasks: BackgroundTasks,
    ) -> JSONResponse | AppointmentFull:
        """Creates a new appointment.

        - Stores it in the DB,
        - Starts a background task to send a confirmation email.
        """
        appointment = Appointment.model_validate(appointment_data)
        with self._db.session() as session:
            session.add(appointment)
            session.commit()
            session.refresh(appointment)
        if appointment_data.payment is not None:
            receipt: CreatePaymentResult = self._square_client.create_payment(
                appointment_data.payment
            )
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
        return self._format_appointment(appointment)

    def view_appointment(self, pubid: str) -> AppointmentFull | JSONResponse:
        try:
            pub_uuid = uuid.UUID(pubid)
        except ValueError:
            return JSONResponse(content=None, status_code=404)
        with self._db.session() as session:
            appointment = session.exec(
                select(Appointment).where(
                    Appointment.pubid == pub_uuid,
                )
            ).first()
            if not appointment:
                return JSONResponse(content=None, status_code=404)
        return self._format_appointment(appointment)

    def _format_appointment(self, appointment: Appointment) -> AppointmentFull:
        return AppointmentFull.extract_pub(
            appointment,
            pub_url=self._linker.view(appointment),
            service=self._service_catalog.get_service(appointment.serviceId),
        )

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
            prefix + "/appointment/{pubid}",
            self.view_appointment,
            methods=["GET"],
            response_model=None,
        )
        app.add_api_route(
            prefix + "/availability",
            self.get_availability,
            methods=["GET"],
        )
