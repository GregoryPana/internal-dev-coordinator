"""Application settings loaded from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "internal-dev-coordinator"
    environment: str = "local"  # local | staging | production

    database_url: str = "postgresql+psycopg://idc:idc@localhost:5432/idc"

    # Dev auth is a login stub ONLY; permission checks are real from day one.
    # The moment a second user logs in, Entra/OIDC becomes mandatory.
    auth_mode: str = "dev"  # dev | entra

    # Freshness threshold in days (FR-023 / status-freshness metric).
    freshness_threshold_days: int = 14

    # AI provider adapter (task T8/T9). Metadata-only inputs; no secrets.
    ai_provider: str = "disabled"  # disabled | anthropic | openai | azure_openai
    ai_model: str = ""


settings = Settings()
