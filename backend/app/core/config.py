from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Insure Plus API"
    app_version: str = "0.1.0"
    debug: bool = False
    allowed_origins: list[str] = ["http://localhost:3000"]

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Database
    database_url: str  # postgresql+asyncpg://user:pass@host:5432/db

    # Azure AI Foundry
    azure_ai_project_connection_string: str
    primary_agent_id: str

    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str

    # Azure Communication Services
    acs_connection_string: str = ""
    acs_sender_address: str = ""

    # Agent run limits
    agent_max_prompt_tokens: int = 4000
    agent_max_completion_tokens: int = 600


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
