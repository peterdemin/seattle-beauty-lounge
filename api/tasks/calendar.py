import datetime
import textwrap

from tenacity import retry, stop_after_delay, wait_fixed

from api.calendar_client import CalendarServiceDummy
from api.constants import TIMEZONE
from api.models import Appointment
from api.service_catalog import ServiceCatalog


class CalendarTask:
    _DESCRIPTION_TEMPLATE = textwrap.dedent(
        """
        Name: {appointment.clientName}
        Phone: {appointment.clientPhone}
        Email: {appointment.clientEmail}
        """
    ).strip()

    def __init__(
        self, calendar_service: CalendarServiceDummy, service_catalog: ServiceCatalog
    ) -> None:
        self._calendar_service = calendar_service
        self._service_catalog = service_catalog

    def create_event(self, appointment: Appointment) -> None:
        self._insert(
            self._service_catalog.compose_event(
                full_index=appointment.serviceId,
                description=self._DESCRIPTION_TEMPLATE.format(appointment=appointment),
                start_dt=TIMEZONE.localize(
                    datetime.datetime.combine(
                        appointment.date,
                        appointment.time,
                    )
                ),
            )
        )

    @retry(stop=stop_after_delay(60), wait=wait_fixed(1))
    def _insert(self, body: dict) -> None:
        self._calendar_service.insert(body)
