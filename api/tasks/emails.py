import datetime
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event
from tenacity import retry, stop_after_delay, wait_fixed

from api.constants import EMAIL, LOCATION, PHONE, TIMEZONE
from api.models import Appointment
from api.service_catalog import ServiceCatalog
from api.smtp_client import SMTPClientDummy
from lib.service import Snippet


class EmailTask:
    _CALENDAR_TEMPLATE = textwrap.dedent(
        f"""
        Seattle Beauty Lounge

        Address: {LOCATION}
        Phone: {PHONE}
        Email: {EMAIL}
        """
    ).strip()

    def __init__(
        self,
        smtp_client: SMTPClientDummy,
        service_catalog: ServiceCatalog,
        email_template: Snippet,
    ) -> None:
        self._smtp_client = smtp_client
        self._service_catalog = service_catalog
        self._email_template = email_template

    def send_confirmation_email(self, appointment: Appointment):
        """Sends a confirmation email to the appointment.clientEmail."""
        self._send(self._compose_confirmation(appointment))

    @retry(stop=stop_after_delay(60), wait=wait_fixed(1))
    def _send(self, message: MIMEMultipart) -> None:
        self._smtp_client.send(message)

    def _compose_confirmation(self, appointment: Appointment) -> MIMEMultipart:
        paragraphs = self._email_template.plain_text.split("\n\n")
        subject = paragraphs[0]
        template = "\n\n".join(paragraphs[1:]).strip()
        mixed = MIMEMultipart("mixed")
        mixed["Subject"] = subject
        mixed["From"] = EMAIL
        mixed["To"] = appointment.clientEmail
        alternative = MIMEMultipart("alternative")
        alternative.attach(
            MIMEText(
                template.format(
                    appointment=appointment,
                    title=self._service_catalog.get_title(appointment.serviceId),
                    date_str=appointment.date.strftime("%A, %B %-d"),
                    time_str=appointment.time.strftime("%I:%M %p"),
                )
            )
        )
        alternative.attach(
            MIMEText(
                self._email_template.html.format(
                    appointment=appointment,
                    title=self._service_catalog.get_title(appointment.serviceId),
                    date_str=appointment.date.strftime("%A, %B %-d"),
                    time_str=appointment.time.strftime("%I:%M %p"),
                ),
                "html",
            )
        )
        mixed.attach(alternative)
        part = MIMEText(
            self._compose_ics(appointment),
            "calendar",
            "utf-8",
        )
        part["Content-Disposition"] = 'attachment; filename="invite.ics"'
        mixed.attach(part)
        return mixed

    def _compose_ics(self, appointment: Appointment) -> str:
        start = TIMEZONE.localize(
            datetime.datetime.combine(
                appointment.date,
                appointment.time,
            )
        )
        end = start + self._service_catalog.get_duration(appointment.serviceId)
        calendar = Calendar()
        calendar.events.append(
            Event(
                summary=self._service_catalog.get_title(appointment.serviceId),
                description=self._CALENDAR_TEMPLATE.format(appointment=appointment),
                location=LOCATION,
                contacts=[PHONE, EMAIL],
                start=start.isoformat(),
                end=end.isoformat(),
            ),
        )
        return IcsCalendarStream.calendar_to_ics(calendar)
