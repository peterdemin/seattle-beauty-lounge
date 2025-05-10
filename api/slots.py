import datetime
import json
import os
import pickle
import time
from typing import Iterable, Optional

from cachetools import TTLCache, cached
from dateutil.parser import parse

from api.calendar_client import DayBreaker, DayBreakerInterface
from api.constants import TIMEZONE
from api.kv import KiwiStore

HERE = os.path.dirname(__file__)


class FreshDayBreaker(DayBreakerInterface):
    TTL = 60  # 1 minute

    def __init__(self, kv: KiwiStore) -> None:
        self._kv = kv
        self._stale_day_breaker = DayBreaker({})
        self._refresh_time = 0

    def break_availability(self, date: str, start: str, end: str) -> list[list[str]]:
        now = time.time()
        if now > self._refresh_time:
            self._stale_day_breaker = DayBreaker(json.loads(self._kv.get("busy_dates") or "{}"))
            self._refresh_time = now + self.TTL
        return self._stale_day_breaker.break_availability(date, start, end)


class SlotsLoader:
    HOURS_FILE = "source/7-media/05-hours-of-operation.rst"
    HOURS_PICKLE = os.path.join(HERE, "hours.pkl")
    LOOKAHEAD = 7 * 6  # 6 weeks

    def __init__(
        self,
        day_breaker: DayBreakerInterface,
        hours_of_operation: Optional[dict[int, list[datetime.time]]] = None,
    ) -> None:
        self._hours_of_operation = hours_of_operation or self.load_hours_of_operation()
        self._day_breaker = day_breaker

    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def gen_ranges(self, today: Optional[datetime.date] = None) -> dict[str, list[list[str]]]:
        """Generates availability time ranges for each day.

        The result is used by the Javascript frontend to dynamically
        generate a list of time slots for duration of a selected service.

        Args:
            today - optional date to anchor the date range. Today be default.

        Returns:
            mapping from date string formatted as "YYYY-mm-dd"
            to a list of (start, end) time pairs formatted as "HH:MM"
        """
        if today is None:
            now = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(TIMEZONE)
            today = now.date()
        hours = self._hours_of_operation
        result = {}
        for offset in range(self.LOOKAHEAD + 1):
            date = today + datetime.timedelta(days=offset)
            date_str = date.strftime("%Y-%m-%d")
            if dow_range := hours.get(date.weekday()):
                start, end = dow_range
                result[date_str] = self._day_breaker.break_availability(
                    date_str,
                    start.strftime("%H:%M"),
                    end.strftime("%H:%M"),
                )
            else:
                result[date_str] = []
        return result

    @classmethod
    def load(cls, day_breaker: DayBreakerInterface) -> "SlotsLoader":
        with open(cls.HOURS_PICKLE, "rb") as fobj:
            return cls(day_breaker, pickle.load(fobj))

    @classmethod
    def dump(cls) -> None:
        with open(cls.HOURS_PICKLE, "wb") as fobj:
            pickle.dump(cls.load_hours_of_operation(), fobj)

    @classmethod
    def load_hours_of_operation(cls) -> dict[int, list[datetime.time]]:
        return {day["weekday"]: [day["start"], day["end"]] for day in cls._iter_hours()}

    @classmethod
    def _iter_hours(cls, hours_file: str = "") -> Iterable[dict]:
        with open(hours_file or cls.HOURS_FILE, "rt", encoding="utf-8") as fobj:
            for line in fobj:
                if not line.strip():
                    continue
                parts = line.strip().split(None, 1)
                if len(parts) != 2:
                    continue
                day_str, hours = parts
                hours_parts = hours.strip().split("-")
                if len(hours_parts) != 2:
                    continue
                start_str, end_str = [x.strip() for x in hours_parts]
                yield {
                    "weekday": parse(day_str.strip()).weekday(),
                    "start": parse(start_str.strip()).time(),
                    "end": parse(end_str.strip()).time(),
                }


if __name__ == "__main__":
    SlotsLoader.dump()
