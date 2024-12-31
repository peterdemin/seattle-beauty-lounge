import json
from typing import cast

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow


class GoogleAuth:
    _SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, client_config: str) -> None:
        self._client_config = json.loads(client_config)

    def get_local_credentials(self) -> Credentials:
        creds = None
        fresh = False
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    pass
                else:
                    fresh = True
            if not fresh:
                flow = InstalledAppFlow.from_client_config(self._client_config, self._SCOPES)
                creds = cast(Credentials, flow.run_local_server(port=0))
        return creds

    def get_different_credentials(self, access_token, refresh_token, client_id, client_secret):
        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )

    def gen_auth_url(self, redirect_uri: str) -> str:
        flow = Flow.from_client_config(
            self._client_config,
            scopes=self._SCOPES,
            redirect_uri=redirect_uri,
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        return auth_url

    def resolve_credentials(self, url: str):
        flow = Flow.from_client_config(
            self._client_config,
            scopes=self._SCOPES,
            redirect_uri="http://localhost:8000/oauth2callback",
        )
        flow.fetch_token(authorization_response=url)
        return flow.credentials
