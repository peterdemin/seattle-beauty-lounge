import stripe
from fastapi import FastAPI


class PaymentAPI:
    PRODUCT_NAME = "Seattle Beauty Lounge Deposit"
    PRICE = 50

    def __init__(self, return_url: str, api_key: str) -> None:
        self._return_url = return_url
        self._api_key = api_key

    def checkout(self) -> dict:
        if not self._api_key:
            return {"error": "Stripe API not configured"}, 422
        stripe.api_key = self._api_key
        stripe.api_version = "2024-12-18.acacia; custom_checkout_beta=v1;"
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "product_data": {"name": self.PRODUCT_NAME},
                        "unit_amount": self.PRICE,
                        "currency": "usd",
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            ui_mode="custom",
            return_url=self._return_url,
        )
        return {"clientSecret": session["client_secret"]}

    def register(self, app_: FastAPI, prefix: str = "") -> None:
        app_.add_api_route(
            prefix + "/checkout",
            self.checkout,
            methods=["POST"],
        )