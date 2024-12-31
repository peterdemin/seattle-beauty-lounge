from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/authorize")
def authorize_user():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/oauth2callback",  # your callback
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
def oauth2callback(request: Request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri="http://localhost:8000/oauth2callback"
    )
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    # Store these securely (DB), especially refresh_token
    access_token = credentials.token
    refresh_token = credentials.refresh_token

    # The user is now authorized; proceed as needed
    return {"msg": "Authorization successful!"}
