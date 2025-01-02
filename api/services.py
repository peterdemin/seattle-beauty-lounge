import datetime
import glob
import os
import pickle
import re
from typing import Iterable, Optional

from api.constants import TIMEZONE_STR

HERE = os.path.dirname(__file__)


class ServicesInfo:
    SERVICES_DIR = "source/services"
    SERVICES_PICKLE = os.path.join(HERE, "services.pkl")
    RE_NUMBER = re.compile(r"(\d+).*")

    def __init__(
        self,
        services: Optional[dict[str, dict]] = None,
    ) -> None:
        self._services = services or self.load_services()

    @classmethod
    def load(cls) -> "ServicesInfo":
        with open(cls.SERVICES_PICKLE, "rb") as fobj:
            return cls(pickle.load(fobj))

    @classmethod
    def dump(cls) -> None:
        with open(cls.SERVICES_PICKLE, "wb") as fobj:
            pickle.dump(cls.load_services(), fobj)

    @classmethod
    def load_services(cls) -> dict[str, dict]:
        return {service["title"]: service for service in cls._iter_services()}

    @staticmethod
    def get_file_index(path: str) -> str:
        return os.path.basename(path).split("-", 1)[0]

    @classmethod
    def _iter_services(cls) -> Iterable[dict]:
        for path in sorted(glob.glob(f"{cls.SERVICES_DIR}/*.md")):
            idx = cls.get_file_index(path)
            with open(path, "rt", encoding="utf-8") as fobj:
                lines = [line.strip() for line in fobj]
                price, duration = lines[-1].split(None, 1)
                duration_min = 0
                if mobj := cls.RE_NUMBER.match(duration):
                    duration_min = int(mobj.group(1))
                yield {
                    "serviceId": idx,
                    "title": lines[0].strip(" #"),
                    "price": price,
                    "duration": datetime.timedelta(minutes=duration_min),
                }

    def compose_event(self, title: str, description: str, start_dt: datetime.datetime) -> dict:
        service = self._services[title]
        # Google Calendar doesn't like non-UTC datetimes
        start_utc = start_dt.astimezone(datetime.timezone.utc)
        return {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_utc.isoformat(),
                "timeZone": TIMEZONE_STR,
            },
            "end": {
                "dateTime": (start_utc + service["duration"]).isoformat(),
                "timeZone": TIMEZONE_STR,
            },
        }


if __name__ == "__main__":
    ServicesInfo.dump()
