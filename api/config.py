from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///api/test.db"

    sender_email: str = ""
    sender_password: str = ""
    enable_emails: bool = False

    proxy_frontend: bool = False
    location_prefix: str = ""

    stripe_api_key: str = ""

    gcp_client_config: str = ""

    @classmethod
    def test_settings(cls) -> "Settings":
        return cls(
            database_url="sqlite://",
            sender_email="",
            sender_password="",
            enable_emails=False,
            proxy_frontend=False,
            location_prefix="",
            stripe_api_key="",
            gcp_client_config="",
        )
