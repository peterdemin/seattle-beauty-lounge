import smtplib
import ssl
from email.message import EmailMessage

from api.models import Appointment


class EmailTaskDummy:

    def send_confirmation_email(self, appointment: Appointment):
        del appointment


class EmailTask(EmailTaskDummy):
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self, sender_email: str, sender_password: str) -> None:
        self._sender_email = sender_email
        self._sender_password = sender_password

    def send_confirmation_email(self, appointment: Appointment):
        """Sends a confirmation email to the appointment.clientEmail."""
        self._send(self._compose_confirmation(appointment))

    def _send(self, msg: EmailMessage) -> None:
        context = ssl.create_default_context()
        with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as smtp:
            smtp.starttls(context=context)
            smtp.login(self._sender_email, self._sender_password)
            smtp.send_message(msg)

    def _compose_confirmation(self, appointment: Appointment) -> EmailMessage:
        subject = "Your Appointment with Seattle Beauty Lounge is Confirmed"
        body = (
            f"Hello {appointment.clientName},\n\n"
            f"Your appointment has been booked.\n"
            f"Service ID: {appointment.serviceId}\n"
            f"Date: {appointment.date}\n"
            f"Time: {appointment.time}\n\n"
            "Thank you for choosing Seattle Beauty Lounge!\n"
        )
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._sender_email
        msg["To"] = appointment.clientEmail
        msg.set_content(body)
        return msg
