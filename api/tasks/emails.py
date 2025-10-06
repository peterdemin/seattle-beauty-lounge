import datetime
import textwrap
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event
from tenacity import retry, stop_after_delay, wait_fixed

from api.constants import EMAIL, LOCATION, PHONE, TIMEZONE, TITLE
from api.models import Appointment
from api.service_catalog import ServiceCatalog
from api.smtp_client import SMTPClientDummy
from lib.service import Snippet


class EmailTask:
    _CALENDAR_TEMPLATE = textwrap.dedent(
        f"""
        {TITLE}

        Address: {LOCATION}
        Phone: {PHONE}
        Email: {EMAIL}
        """
    ).strip()
    _OWNER_NOTIFICATION_TEMPLATE = textwrap.dedent(
        f"""
        {TITLE}

        Appointment: {{admin_url}}

        Service: {{title}}
        Date: {{date_str}}
        Time: {{time_str}}

        Name: {{appointment.clientName}}
        Phone: {{appointment.clientPhone}}
        Email: {{appointment.clientEmail}}
        """
    ).strip()

    def __init__(
        self,
        smtp_client: SMTPClientDummy,
        service_catalog: ServiceCatalog,
        email_template: Snippet,
        admin_url: str,
    ) -> None:
        self._smtp_client = smtp_client
        self._service_catalog = service_catalog
        self._email_template = email_template
        self._admin_url_template = f"{admin_url}?app={{appointment.id}}"

    def on_appointment(self, appointment: Appointment) -> None:
        """Sends a confirmation email client and notification to the owner."""
        self._send(self._compose_confirmation(appointment))
        self._send(self._compose_owner_notification_email(appointment))

    @retry(stop=stop_after_delay(60), wait=wait_fixed(1))
    def _send(self, message: Message) -> None:
        self._smtp_client.send(message)

    def _compose_owner_notification_email(self, appointment: Appointment) -> MIMEText:
        msg = MIMEText(
            self._OWNER_NOTIFICATION_TEMPLATE.format(
                appointment=appointment,
                title=self._service_catalog.get_title(appointment.serviceId),
                date_str=appointment.date.strftime("%A, %B %-d"),
                time_str=appointment.time.strftime("%I:%M %p"),
                admin_url=self._admin_url_template.format(appointment=appointment),
            )
        )
        msg["Subject"] = f"New appointment in {TITLE}"
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        return msg

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
        return IcsCalendarStream.calendar_to_ics(
            Calendar(
                events=[  # pyright: ignore[reportCallIssue]
                    Event(
                        summary=self._service_catalog.get_title(appointment.serviceId),
                        description=self._CALENDAR_TEMPLATE.format(appointment=appointment),
                        location=LOCATION,
                        contacts=[PHONE, EMAIL],
                        start=start.isoformat(),
                        end=end.isoformat(),
                    ),
                ]
            )
        )
