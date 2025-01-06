from twilio.rest import Client


class SMSClientDummy:
    def send(self, phone_number: str, message: str) -> None:
        del phone_number, message


class SMSClient(SMSClientDummy):
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        self._client = Client(account_sid, auth_token)
        self._from_number = from_number

    def send(self, phone_number: str, message: str) -> None:
        self._client.messages.create(
            from_=self._from_number,
            body=message,
            to=phone_number,
        )
