import json
import os
import sys
from pprint import pprint
from typing import cast

from google.oauth2.credentials import Credentials

from api.calendar_client import CalendarEventParser, CalendarFetcher, DayBreaker
from api.config import Settings
from api.db import Database
from api.google_auth import GoogleAuth
from api.kv import KiwiStore


class CalendarSynchronizer:
    def __init__(
        self,
        kv: KiwiStore,
        calendar_fetcher: CalendarFetcher,
        calendar_event_parser: CalendarEventParser,
        day_breaker: DayBreaker,
    ) -> None:
        self._kv = kv
        self._calendar_fetcher = calendar_fetcher
        self._calendar_event_parser = calendar_event_parser
        self._day_breaker = day_breaker

    def sync(self, limit: int = 7) -> None:
        events = self._calendar_fetcher(limit)
        self._kv.set("events", json.dumps(events))
        by_date = self._day_breaker.group_time_ranges(
            [self._calendar_event_parser(event) for event in events]
        )
        self._kv.set("busy_dates", json.dumps(by_date))
        pprint(by_date)

    def load_creds(self, email: str) -> Credentials:
        if local_creds := GoogleAuth.delegated(email):
            return cast(Credentials, local_creds)

        if local_creds_json := self._kv.get("local_creds"):
            return Credentials.from_authorized_user_info(
                json.loads(local_creds_json), scopes=GoogleAuth._SCOPES
            )

        with open(os.path.expanduser("~/.gcp/credentials.json"), "rt", encoding="utf-8") as fobj:
            client_config = fobj.read()
        local_creds = GoogleAuth(client_config).get_local_credentials()
        self._kv.set("local_creds", local_creds.to_json())
        return local_creds


def main(email: str):
    cal = CalendarSynchronizer(
        kv=KiwiStore(db=Database(database_url=Settings().database_url)),
        calendar_fetcher=CalendarFetcher(cast(Credentials, GoogleAuth.delegated(email))),
        calendar_event_parser=CalendarEventParser(),
        day_breaker=DayBreaker({}),
    )
    cal.sync()


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "peter@seattle-beauty-lounge.com"
    main(email)
