import json

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from api.google_auth import GoogleAuth
from api.kv import KiwiStore

app = FastAPI()


class BackofficeAPI:
    def __init__(self, kv: KiwiStore, google_auth: GoogleAuth) -> None:
        self._kv = kv
        self._google_auth = google_auth

    def authorize_user(self, request: Request) -> RedirectResponse:
        return RedirectResponse(
            self._google_auth.gen_auth_url(
                redirect_uri=self._get_redirect_uri(request),
            )
        )

    def oauth2callback(self, request: Request):
        self._kv.set(
            "creds",
            json.dumps(
                self._google_auth.resolve_credentials(
                    str(request.url.replace(scheme="https")),
                    redirect_uri=self._get_redirect_uri(request),
                ).to_json()
            ),
        )
        return "Authorization successful!"

    def _get_redirect_uri(self, request: Request) -> str:
        return str(request.url_for("oauth2callback").replace(scheme="https"))

    def register(self, app_: FastAPI, prefix: str = "") -> None:
        app_.add_api_route(
            prefix + "/auth/consent",
            self.authorize_user,
            methods=["GET"],
        )
        app_.add_api_route(
            prefix + "/auth/success",
            self.oauth2callback,
            methods=["GET"],
        )
