import datetime

from api.constants import TIMEZONE_STR
from api.services import ServicesInfo

MICROBLADING_EVENT = {
    "summary": "Eyebrow microblading",
    "description": "Description",
    "start": {"dateTime": "2014-04-14T01:02:03", "timeZone": TIMEZONE_STR},
    "end": {"dateTime": "2014-04-14T04:02:03", "timeZone": TIMEZONE_STR},
}


def test_load_from_pickle():
    services_info = ServicesInfo.load()
    event = services_info.compose_event(
        "Eyebrow microblading",
        "Description",
        datetime.datetime(2014, 4, 14, 1, 2, 3),
    )
    assert event == MICROBLADING_EVENT
