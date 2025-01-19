import uuid

from pydantic import BaseModel
from square.client import Client


class Payment(BaseModel):
    token: str
    idempotencyKey: str


class SquareClient:
    USER_AGENT = "python3.12"
    DEPOSIT_CENTS = 5000  # $50.00
    CURRENCY = "USD"
    COUNTRY = "US"

    def __init__(
        self,
        application_id: str,
        square_environment: str,
        square_location_id: str,
        access_token: str,
    ) -> None:
        self._application_id = application_id
        self._client = Client(
            access_token=access_token,
            environment=square_environment,
            user_agent_detail=self.USER_AGENT,
        )
        self._location_id = square_location_id

    def bootstrap(self) -> dict:
        return {
            "applicationId": self._application_id,
            "locationId": self._location_id,
            "currency": self.CURRENCY,
            "country": self.COUNTRY,
            "idempotencyKey": str(uuid.uuid4()),
        }

    def create_payment(self, payment: Payment) -> dict:
        if not self._client.payments:
            return {}
        create_payment_response = self._client.payments.create_payment(
            body={
                "source_id": payment.token,
                "idempotency_key": payment.idempotencyKey,
                "amount_money": {
                    "amount": self.DEPOSIT_CENTS,
                    "currency": self.CURRENCY,
                },
            }
        )
        if create_payment_response.is_success():
            return create_payment_response.body
        return {"error": create_payment_response.errors[0]["detail"]}
