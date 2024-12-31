import os

from fastapi import Request
from fastapi.responses import RedirectResponse
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleAuth:
    _CREDENTIALS_PATH = os.path.expanduser("~/.gcp/credentials.json")

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
                flow = InstalledAppFlow.from_client_secrets_file(self._CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
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

    def authorize_user(self):
        flow = Flow.from_client_secrets_file(
            self._CREDENTIALS_PATH,
            scopes=SCOPES,
            redirect_uri="http://localhost:8000/oauth2callback",  # your callback
        )
        auth_url, _ = flow.authorization_url(prompt="consent")
        return RedirectResponse(auth_url)

    def oauth2callback(self, request: Request):
        flow = Flow.from_client_secrets_file(
            self._CREDENTIALS_PATH,
            scopes=SCOPES,
            redirect_uri="http://localhost:8000/oauth2callback",
        )
        flow.fetch_token(authorization_response=str(request.url))
        credentials = flow.credentials

        # Store these securely (DB), especially refresh_token
        access_token = credentials.token
        refresh_token = credentials.refresh_token

        # The user is now authorized; proceed as needed
        return {"msg": "Authorization successful!"}
