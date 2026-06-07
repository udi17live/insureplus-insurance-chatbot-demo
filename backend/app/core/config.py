from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from functools import lru_cache
import json


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
    allowed_origins_raw: str = "http://localhost:3000"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Database
    database_url: str  # postgresql+asyncpg://user:pass@host:5432/db

    # Azure AI Foundry
    azure_ai_project_base_endpoint: str   # project base URL for AIProjectClient
    primary_agent_id: str                 # agent name, e.g. "insureplus-rg-main"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Agent response limit
    agent_max_completion_tokens: int = 600

    # Agent tool API key (used by Foundry to authenticate tool calls)
    agent_api_key: str = ""

    @property
    def allowed_origins(self) -> list[str]:
        v = self.allowed_origins_raw.strip().strip("'\"")
        if v.startswith("["):
            return json.loads(v)
        return [o.strip() for o in v.split(",") if o.strip()]

    @property
    def agent_reference(self) -> dict:
        return {"name": self.primary_agent_id, "type": "agent_reference"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
