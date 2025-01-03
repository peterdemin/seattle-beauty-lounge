import datetime
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event

from api.constants import EMAIL, LOCATION, PHONE, TIMEZONE
from api.models import Appointment
from api.services import ServicesInfo
from api.smtp_client import SMTPClientDummy


class EmailTask:
    _CALENDAR_TEMPLATE = textwrap.dedent(
        f"""
        Seattle Beauty Lounge

        Address: {LOCATION}
        Phone: {PHONE}
        Email: {EMAIL}
        """
    ).strip()
    _EMAIL_TEMPLATE = textwrap.dedent(
        f"""
        Hello {{appointment.clientName}},

        Your appointment has been booked.

        We'll see you on {{date_str}} at {{time_str}} for {{appointment.serviceId}}.

        Thank you for choosing Seattle Beauty Lounge!

        Address: {LOCATION}
        Phone: {PHONE}
        Email: {EMAIL}
        """
    ).strip()

    def __init__(
        self,
        smtp_client: SMTPClientDummy,
        services_info: ServicesInfo,
    ) -> None:
        self._smtp_client = smtp_client
        self._services_info = services_info

    def send_confirmation_email(self, appointment: Appointment):
        """Sends a confirmation email to the appointment.clientEmail."""
        self._smtp_client.send(self._compose_confirmation(appointment))

    def _compose_confirmation(self, appointment: Appointment) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["Subject"] = "Appointment with Seattle Beauty Lounge"
        msg["From"] = EMAIL
        msg["To"] = appointment.clientEmail
        msg.attach(
            MIMEText(
                self._EMAIL_TEMPLATE.format(
                    appointment=appointment,
                    date_str=appointment.date.strftime("%A, %B %d"),
                    time_str=appointment.time.strftime("%H:%M"),
                )
            )
        )
        part = MIMEText(
            self._compose_ics(appointment),
            "calendar",
            "utf-8",
        )
        part["Content-Disposition"] = 'attachment; filename="invite.ics"'
        msg.attach(part)
        return msg

    def _compose_ics(self, appointment: Appointment) -> str:
        start = TIMEZONE.localize(
            datetime.datetime.combine(
                appointment.date,
                appointment.time,
            )
        )
        end = start + self._services_info.get_duration(appointment.serviceId)
        calendar = Calendar()
        calendar.events.append(
            Event(
                summary=appointment.serviceId,
                description=self._CALENDAR_TEMPLATE.format(appointment=appointment),
                location=LOCATION,
                contacts=[PHONE, EMAIL],
                start=start.isoformat(),
                end=end.isoformat(),
            ),
        )
        return IcsCalendarStream.calendar_to_ics(calendar)
