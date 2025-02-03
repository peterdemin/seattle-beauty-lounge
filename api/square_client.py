from pydantic import BaseModel
from square.client import Client


class Payment(BaseModel):
    token: str
    idempotencyKey: str


class SquareClientDummy:

    def create_payment(self, payment: Payment) -> dict:
        if not payment.token:
            return {"error": "no token"}
        return {
            "payment": {
                "id": "J2xeb9aj55wS755Tw59hmjRKK3ZZY",
                "created_at": "2025-02-03T04:49:12.112Z",
                "updated_at": "2025-02-03T04:49:12.340Z",
                "amount_money": {"amount": 5000, "currency": "USD"},
                "status": "COMPLETED",
                "delay_duration": "PT168H",
                "source_type": "CARD",
                "card_details": {
                    "status": "CAPTURED",
                    "card": {
                        "card_brand": "VISA",
                        "last_4": "1111",
                        "exp_month": 10,
                        "exp_year": 2030,
                        "fingerprint": "sq-1-IIAv2hH5VALaWZ5D0-vmIUAtH88q9xfkX-64tGz4jvoQZi4r0Z2xelzccPVo3SSz4g",
                        "card_type": "CREDIT",
                        "prepaid_type": "NOT_PREPAID",
                        "bin": "411111",
                    },
                    "entry_method": "KEYED",
                    "cvv_status": "CVV_ACCEPTED",
                    "avs_status": "AVS_ACCEPTED",
                    "statement_description": "SQ *DEFAULT TEST ACCOUNT",
                    "card_payment_timeline": {
                        "authorized_at": "2025-02-03T04:49:12.245Z",
                        "captured_at": "2025-02-03T04:49:12.340Z",
                    },
                },
                "location_id": "LH4TW6RJVR0M7",
                "order_id": "zIt3tz8zcl3o6SbMIUeQ56ULaYbZY",
                "risk_evaluation": {
                    "created_at": "2025-02-03T04:49:12.245Z",
                    "risk_level": "NORMAL",
                },
                "total_money": {"amount": 5000, "currency": "USD"},
                "approved_money": {"amount": 5000, "currency": "USD"},
                "receipt_number": "J2xe",
                "receipt_url": "https://squareupsandbox.com/receipt/preview/J2xeb9aj55wS755Tw59hmjRKK3ZZY",
                "delay_action": "CANCEL",
                "delayed_until": "2025-02-10T04:49:12.112Z",
                "application_details": {
                    "square_product": "ECOMMERCE_API",
                    "application_id": "sandbox-sq0idb-GCjOz8Fsffi2kHv4wUNEkA",
                },
                "version_token": "TD2eGbKi3ZkaluQJ2vs4UnIVoDJxsNscu4zKTTMdQNe6o",
            }
        }


class SquareClient(SquareClientDummy):
    USER_AGENT = "python3.12"
    DEPOSIT_CENTS = 5000  # $50.00
    CURRENCY = "USD"
    COUNTRY = "US"

    def __init__(
        self,
        square_environment: str,
        access_token: str,
    ) -> None:
        self._client = Client(
            access_token=access_token,
            environment=square_environment,
            user_agent_detail=self.USER_AGENT,
        )

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
