import datetime
import textwrap

from api.calendar_client import CalendarServiceDummy
from api.constants import TIMEZONE
from api.models import Appointment
from api.services import ServicesInfo


class CalendarTask:
    _DESCRIPTION_TEMPLATE = textwrap.dedent(
        """
        Name: {appointment.clientName}
        Phone: {appointment.clientPhone}
        Email: {appointment.clientEmail}
        """
    ).strip()

    def __init__(self, calendar_service: CalendarServiceDummy, services_info: ServicesInfo) -> None:
        self._calendar_service = calendar_service
        self._services_info = services_info

    def create_event(self, appointment: Appointment) -> None:
        self._calendar_service.insert(
            self._services_info.compose_event(
                title=appointment.serviceId,
                description=self._DESCRIPTION_TEMPLATE.format(appointment=appointment),
                start_dt=TIMEZONE.localize(
                    datetime.datetime.combine(
                        appointment.date,
                        appointment.time,
                    )
                ),
            )
        )
