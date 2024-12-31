import json
from typing import cast

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow


class GoogleAuth:
    _SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, client_config: str) -> None:
        self._client_config = json.loads(client_config)

    def get_local_credentials(self) -> Credentials:
        flow = InstalledAppFlow.from_client_config(self._client_config, self._SCOPES)
        return cast(Credentials, flow.run_local_server(port=0))

    def gen_auth_url(self, redirect_uri: str) -> str:
        flow = Flow.from_client_config(
            self._client_config,
            scopes=self._SCOPES,
            redirect_uri=redirect_uri,
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        return auth_url

    def resolve_credentials(self, url: str) -> Credentials:
        flow = Flow.from_client_config(
            self._client_config,
            scopes=self._SCOPES,
            redirect_uri="http://localhost:8000/oauth2callback",
        )
        flow.fetch_token(authorization_response=url)
        return cast(Credentials, flow.credentials)
