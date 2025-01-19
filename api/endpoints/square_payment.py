from fastapi import FastAPI

from api.square_client import Payment, SquareClient


class SquarePaymentAPI:

    def __init__(self, square_client: SquareClient) -> None:
        self._square_client = square_client

    def bootstrap(self) -> dict:
        return self._square_client.bootstrap()

    def pay(self, payment: Payment) -> dict:
        return self._square_client.create_payment(payment)

    def register(self, app: FastAPI, prefix: str = "") -> None:
        app.add_api_route(
            prefix + "/bootstrap",
            self.bootstrap,
            methods=["POST"],
        )
        app.add_api_route(
            prefix + "/pay",
            self.pay,
            methods=["POST"],
        )
