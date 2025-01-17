import datetime

from api.constants import TIMEZONE, TIMEZONE_STR
from api.service_catalog import ServiceCatalog

MICROBLADING_EVENT = {
    "summary": "Eyebrow microblading",
    "description": "Description",
    "start": {"dateTime": "2014-04-14T01:02:03-07:00", "timeZone": TIMEZONE_STR},
    "end": {"dateTime": "2014-04-14T04:02:03-07:00", "timeZone": TIMEZONE_STR},
}


def test_load_from_pickle():
    service_catalog = ServiceCatalog()
    event = service_catalog.compose_event(
        full_index="2.04",
        description="Description",
        start_dt=TIMEZONE.localize(
            datetime.datetime.combine(
                datetime.date(2014, 4, 14),
                datetime.time(1, 2, 3),
            )
        ),
    )
    assert event == MICROBLADING_EVENT
