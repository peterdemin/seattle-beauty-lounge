import json

from api.calendar_client import CalendarEventParser, CalendarFetcher, DayBreaker
from api.kv import KiwiStore


class AvailabilityTask:
    def __init__(
        self,
        key: str,
        kv: KiwiStore,
        calendar_fetcher: CalendarFetcher,
        calendar_event_parser: CalendarEventParser,
        day_breaker: DayBreaker,
    ) -> None:
        self._key = key
        self._kv = kv
        self._calendar_fetcher = calendar_fetcher
        self._calendar_event_parser = calendar_event_parser
        self._day_breaker = day_breaker

    def __call__(self, limit: int = 7 * 7) -> None:
        self._kv.set(
            self._key,
            json.dumps(
                self._day_breaker.group_time_ranges(
                    map(
                        self._calendar_event_parser,
                        self._calendar_fetcher(limit),
                    )
                )
            ),
        )