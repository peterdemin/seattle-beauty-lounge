from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    base_url: str = ""
    database_url: str = "sqlite:///api/test.db"
    proxy_frontend: bool = False
    location_prefix: str = ""

    sender_email: str = ""
    sender_password: str = ""
    enable_emails: bool = False
    enable_calendar: bool = False

    square_access_token: str = ""
    square_environment: str = ""
    sentry_dsn: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    admin_url: str = ""
    enable_admin: bool = False
    enable_build: bool = False

    @classmethod
    def test_settings(cls) -> "Settings":
        return cls(
            base_url="http://localhost:8000/",
            database_url="sqlite://",
            sender_email="",
            sender_password="",
            enable_emails=False,
            enable_calendar=False,
            proxy_frontend=False,
            location_prefix="",
            square_access_token="",
            square_environment="test",
            sentry_dsn="",
            twilio_account_sid="",
            twilio_auth_token="",
            twilio_from_number="",
            admin_url="http://localhost:8000/admin.html",
            enable_admin=True,
            enable_build=True,
        )
