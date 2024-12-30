import datetime
import os
import pickle
from typing import Iterable, Optional

from dateutil.parser import parse

HERE = os.path.dirname(__file__)


class SlotsLoader:
    HOURS_FILE = "source/pages/51-hours.md"
    HOURS_PICKLE = os.path.join(HERE, "hours.pkl")
    FIRST_OFFSET = 1
    LAST_OFFSET = 7 * 6  # 6 weeks

    def __init__(self, hours_of_operation: Optional[dict[int, list[datetime.time]]] = None) -> None:
        self._hours_of_operation = hours_of_operation or self.load_hours_of_operation()

    def gen_ranges(self, today: Optional[datetime.date] = None) -> dict[str, list[list[str]]]:
        """Generates availability time ranges for each day.

        The result is used by the Javascript frontend to dynamically
        generate a list of time slots for duration of a selected service.

        Args:
            today - optional date to anchor the date range. Today be default.

        Returns:
            mapping from date string formatted as YYYY-mm-dd
            to a list of start and end time formatted as HH:MM
        """
        today = today or datetime.date.today()
        hours = self._hours_of_operation
        result = {}
        for offset in range(self.FIRST_OFFSET, self.LAST_OFFSET + 1):
            date = today + datetime.timedelta(days=offset)
            if dow_range := hours.get(date.weekday()):
                start, end = dow_range
                result[date.strftime("%Y-%m-%d")] = [
                    [
                        start.strftime("%H:%M"),
                        end.strftime("%H:%M"),
                    ]
                ]
        return result

    @classmethod
    def load(cls) -> "SlotsLoader":
        with open(cls.HOURS_PICKLE, "rb") as fobj:
            return cls(pickle.load(fobj))

    @classmethod
    def dump(cls) -> None:
        with open(cls.HOURS_PICKLE, "wb") as fobj:
            pickle.dump(cls.load_hours_of_operation(), fobj)

    @classmethod
    def load_hours_of_operation(cls) -> dict[int, list[datetime.time]]:
        return {day["weekday"]: [day["start"], day["end"]] for day in cls._iter_hours()}

    @classmethod
    def _iter_hours(cls, hours_file: str = "") -> Iterable[dict]:
        with open(f"{hours_file or cls.HOURS_FILE}", "rt", encoding="utf-8") as fobj:
            for line in fobj:
                if "-" not in line:
                    continue
                day_str, hours = line.strip().split(None, 1)
                day = parse(day_str).weekday()
                start_str, end_str = [x.strip() for x in hours.split("-", 1)]
                start = parse(start_str).time()
                end = parse(end_str).time()
                yield {"weekday": day, "start": start, "end": end}


if __name__ == "__main__":
    SlotsLoader.dump()
