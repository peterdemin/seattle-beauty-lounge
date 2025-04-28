from typing import NotRequired, TypedDict

from pydantic import BaseModel
from square import Square
from square.environment import SquareEnvironment


class Payment(BaseModel):
    token: str
    idempotencyKey: str


class CreatePaymentResult(TypedDict):
    error: NotRequired[str]
    id: NotRequired[str]


class SquareClientDummy:

    def create_payment(self, payment: Payment) -> CreatePaymentResult:
        if not payment.token:
            return {"error": "no token"}
        return {"id": "J2xeb9aj55wS755Tw59hmjRKK3ZZY"}


class SquareClient(SquareClientDummy):
    DEPOSIT_CENTS = 5000  # $50.00
    CURRENCY = "USD"
    COUNTRY = "US"
    _ENV_MAPPING = {
        "sandbox": SquareEnvironment.SANDBOX,
        "production": SquareEnvironment.PRODUCTION,
    }

    def __init__(
        self,
        square_environment: str,
        access_token: str,
    ) -> None:
        self._client = Square(
            environment=self._ENV_MAPPING[square_environment],
            token=access_token,
        )

    def create_payment(self, payment: Payment) -> CreatePaymentResult:
        if not self._client.payments:
            return {}
        create_payment_response = self._client.payments.create(
            source_id=payment.token,
            idempotency_key=payment.idempotencyKey,
            amount_money={
                "amount": self.DEPOSIT_CENTS,
                "currency": self.CURRENCY,
            },
        )
        if create_payment_response.errors:
            return {"error": create_payment_response.errors[0].detail or "Unexpected error"}
        if create_payment_response.payment:
            return {"id": create_payment_response.payment.id or "Missing paymend.id"}
        return {}
