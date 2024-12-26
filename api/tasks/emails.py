import smtplib
import ssl
from email.message import EmailMessage

from api.models import Appointment
from api.config import Settings


class EmailTask:
    def __init__(self, settings: Settings) -> None:
        self._sender_email = settings.sender_email
        self._sender_password = settings.sender_password
        self._enabled = settings.enable_emails

    def send_confirmation_email(self, appointment: Appointment):
        """Sends a confirmation email to the appointment.clientEmail."""
        if not self._enabled:
            return
        subject = "Your Appointment is Confirmed"
        body = (
            f"Hello {appointment.clientName},\n\n"
            f"Your appointment has been booked.\n"
            f"Service ID: {appointment.serviceId}\n"
            f"Date: {appointment.date}\n"
            f"Time: {appointment.time}\n\n"
            "Thank you for choosing our service!\n"
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._sender_email
        msg["To"] = appointment.clientEmail
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(self._sender_email, self._sender_password)
            smtp.send_message(msg)
