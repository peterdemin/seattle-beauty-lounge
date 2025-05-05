import json
import sys
from pprint import pprint
from typing import cast

from google.oauth2.credentials import Credentials

from api.calendar_client import CalendarEventParser, CalendarService, DayBreaker
from api.config import Settings
from api.db import Database
from api.google_auth import GoogleAuth
from api.kv import KiwiStore


class CalendarSynchronizer:
    def __init__(
        self,
        kv: KiwiStore,
        calendar_service: CalendarService,
        calendar_event_parser: CalendarEventParser,
        day_breaker: DayBreaker,
    ) -> None:
        self._kv = kv
        self._calendar_service = calendar_service
        self._calendar_event_parser = calendar_event_parser
        self._day_breaker = day_breaker

    def sync(self, limit) -> None:
        events = self._calendar_service.fetch(limit)
        pprint(events)
        by_date = self._day_breaker.group_time_ranges(
            [self._calendar_event_parser(event) for event in events]
        )
        self._kv.set("busy_dates", json.dumps(by_date))
        pprint(by_date)


def main(email: str):
    cal = CalendarSynchronizer(
        kv=KiwiStore(db=Database(database_url=Settings().database_url)),
        calendar_service=CalendarService(cast(Credentials, GoogleAuth.delegated(email))),
        calendar_event_parser=CalendarEventParser(),
        day_breaker=DayBreaker({}),
    )
    cal.sync(14)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "peter@seattle-beauty-lounge.com")
