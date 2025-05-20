import datetime

import pytest

from api.calendar_client import CalendarServiceDummy, DayBreaker
from api.models import Appointment
from lib.service import ImageInfo, ServiceInfo


@pytest.mark.parametrize(
    "breaks,expected",
    [
        ([["12:00", "13:00"]], [["09:00", "12:00"], ["13:00", "17:00"]]),
        ([["07:00", "10:00"]], [["10:00", "17:00"]]),
        ([["13:00", "20:00"]], [["09:00", "13:00"]]),
        ([["00:00", "23:59"]], []),
        (
            [["12:00", "13:00"], ["14:00", "15:00"]],
            [["09:00", "12:00"], ["13:00", "14:00"], ["15:00", "17:00"]],
        ),
        (
            [["08:00", "11:00"], ["16:00", "18:00"]],
            [["11:00", "16:00"]],
        ),
        (
            [["09:00", "12:00"], ["12:00", "17:00"]],
            [],
        ),
    ],
)
def test_day_breaker_cases(breaks, expected):
    day_breaker = DayBreaker({"2014-04-14": breaks})
    got = day_breaker.break_availability("2014-04-14", "09:00", "17:00")
    assert got == expected


def test_compose_event_example() -> None:
    event = CalendarServiceDummy.compose_event(
        appointment=Appointment(
            id=1,
            serviceId="1.23",
            date=datetime.date(2014, 4, 4),
            time=datetime.time(13, 23, 45),
            clientName="Peter Demin",
            clientPhone="2403421438",
            clientEmail="peterdemin@gmail.com",
        ),
        service_info=ServiceInfo(
            source_path="1-cat/23-name.rst",
            image=ImageInfo.dummy(),
            title="in-and-out",
            duration_min=3,
        ),
        admin_url="http://admin",
    )
    assert event == {
        "description": "Appointment: http://admin\n"
        "Name: Peter Demin\n"
        "Phone: 2403421438\n"
        "Email: peterdemin@gmail.com",
        "end": {"dateTime": "2014-04-04T13:26:45-07:00", "timeZone": "America/Los_Angeles"},
        "start": {"dateTime": "2014-04-04T13:23:45-07:00", "timeZone": "America/Los_Angeles"},
        "summary": "in-and-out",
    }
