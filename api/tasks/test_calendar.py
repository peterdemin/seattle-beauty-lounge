import datetime
from unittest import mock

from pydantic import HttpUrl

from api.calendar_client import CalendarServiceDummy
from api.linker import Linker
from api.models import Appointment
from api.service_catalog import ServiceCatalog
from api.tasks.calendar import CalendarTask
from lib.service import ImageInfo, ServiceInfo


def test_create_calendar_event() -> None:
    calendar_service = mock.Mock(spec=CalendarServiceDummy)
    calendar_service.compose_event.return_value = {"summary": "summary"}
    service_info = ServiceInfo(
        source_path="1-cat/23-name.rst",
        image=ImageInfo.dummy(),
        title="service",
        duration_min=3,
    )
    calendar_task = CalendarTask(
        calendar_service=calendar_service,
        service_catalog=ServiceCatalog([service_info]),
        linker=Linker(base_url="", admin_url="http://admin"),
    )
    appointment = Appointment(
        id=1,
        serviceId="1.23",
        date=datetime.date(2014, 4, 4),
        time=datetime.time(13, 23, 45),
        clientName="clientName",
        clientPhone="clientPhone",
        clientEmail="clientEmail",
    )
    calendar_task.create_event(appointment)
    calendar_service.compose_event.assert_called_once_with(
        appointment=appointment, service_info=service_info, admin_url=HttpUrl("http://admin?app=1")
    )
    calendar_service.insert.assert_called_once_with({"summary": "summary"})
