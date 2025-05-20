import datetime

from api.constants import TIMEZONE_STR
from lib.service import ServiceInfo


class ServiceCatalog:
    def __init__(self, services: list[ServiceInfo]) -> None:
        self._services: dict[str, ServiceInfo] = {s.full_index: s for s in services}

    def compose_event(self, full_index: str, description: str, start_dt: datetime.datetime) -> dict:
        return {
            "summary": self.get_title(full_index),
            "description": description,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": TIMEZONE_STR,
            },
            "end": {
                "dateTime": (start_dt + self.get_duration(full_index)).isoformat(),
                "timeZone": TIMEZONE_STR,
            },
        }

    def get_service(self, full_index: str) -> ServiceInfo:
        return self._services[full_index]

    def get_title(self, full_index: str) -> str:
        return self._services[full_index].title

    def get_duration(self, full_index: str) -> datetime.timedelta:
        return self._services[full_index].delta
