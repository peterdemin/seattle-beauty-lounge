import textwrap

from tenacity import retry, stop_after_delay, wait_fixed

from api.calendar_client import CalendarEventBody, CalendarServiceDummy
from api.models import Appointment
from api.service_catalog import ServiceCatalog


class CalendarTask:
    _DESCRIPTION_TEMPLATE = textwrap.dedent(
        """
        Appointment: {admin_url}
        Name: {appointment.clientName}
        Phone: {appointment.clientPhone}
        Email: {appointment.clientEmail}
        """
    ).strip()

    def __init__(
        self,
        calendar_service: CalendarServiceDummy,
        service_catalog: ServiceCatalog,
        admin_url: str,
    ) -> None:
        self._calendar_service = calendar_service
        self._service_catalog = service_catalog
        self._admin_url_template = f"{admin_url}?app={{appointment.id}}"

    def create_event(self, appointment: Appointment) -> None:
        self._insert(
            self._calendar_service.compose_event(
                appointment=appointment,
                service_info=self._service_catalog.get_service(appointment.serviceId),
                admin_url=self._admin_url_template.format(appointment=appointment),
            )
        )

    @retry(stop=stop_after_delay(60), wait=wait_fixed(1))
    def _insert(self, body: CalendarEventBody) -> None:
        self._calendar_service.insert(body)
