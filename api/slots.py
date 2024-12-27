from typing import Iterable

from dateutil.parser import parse


class SlotsLoader:
    HOURS_FILE = "source/pages/51-hours.md"
    FIRST_OFFSET = 1
    LAST_OFFSET = 7 * 6  # 6 weeks

    def load_slots(self) -> Iterable[dict]:
        yield {}
        return

    def iter_hours(self) -> Iterable[dict]:
        with open(f"{self.HOURS_FILE}", "rt", encoding="utf-8") as fobj:
            for line in fobj:
                if "-" not in line:
                    continue
                day, hours = line.strip().split(None, 1)
                start_str, end_str = [x.strip() for x in hours.split("-", 1)]
                start = parse(start_str).time()
                end = parse(end_str).time()
                yield {"day": day, "start": start, "end": end}
