import smtplib
import ssl
from email.message import Message


class SMTPClientDummy:

    def send(self, msg: Message) -> None:
        del msg


class SMTPClient(SMTPClientDummy):
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(
        self,
        sender_email: str,
        sender_password: str,
    ) -> None:
        self._sender_email = sender_email
        self._sender_password = sender_password

    def send(self, msg: Message) -> None:
        context = ssl.create_default_context()
        with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as smtp:
            smtp.starttls(context=context)
            smtp.login(self._sender_email, self._sender_password)
            smtp.send_message(msg)
