from pydantic import HttpUrl

from api.models import Appointment


class Linker:
    def __init__(self, *, base_url: str, admin_url: str) -> None:
        self._base_url = base_url
        self._admin_url = admin_url

    def view(self, appointment: Appointment) -> HttpUrl:
        return HttpUrl(f"{self._base_url}/appointment.html?app={appointment.pubid}")

    def admin(self, appointment: Appointment) -> HttpUrl:
        return HttpUrl(f"{self._admin_url}?app={appointment.id}")
