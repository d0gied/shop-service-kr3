from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn


class DatabaseSettings(BaseSettings):
    """Database settings for the payments service."""

    database_url: PostgresDsn = PostgresDsn(
        "postgresql://user:password@localhost:5432/payments"
    )
    echo: bool = False
