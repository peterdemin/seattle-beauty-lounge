from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///api/test.db"

    sender_email: str = ""
    sender_password: str = ""
    enable_emails: bool = False

    proxy_frontend: bool = False
