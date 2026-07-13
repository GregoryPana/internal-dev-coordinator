"""Application settings loaded from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # IDC_ prefix namespaces all env vars: other projects on this machine
    # export bare DATABASE_URL etc., which must never leak into this app.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="IDC_", extra="ignore"
    )

    app_name: str = "internal-dev-coordinator"
    environment: str = "local"  # local | staging | production

    database_url: str = "postgresql+psycopg://idc:idc@localhost:5455/idc"

    # Dev auth is a login stub ONLY; permission checks are real from day one.
    # The moment a second user logs in, Entra/OIDC becomes mandatory.
    auth_mode: str = "dev"  # dev | entra
    dev_default_user_email: str = "gregory.panagary@cwseychelles.com"

    # Freshness threshold in days (FR-023 / status-freshness metric).
    freshness_threshold_days: int = 14

    # AI provider adapter (task T8/T9). Metadata-only inputs; no secrets.
    ai_provider: str = "disabled"  # disabled | openrouter | anthropic | openai | azure_openai
    ai_model: str = ""
    # Never logged, never stored in the DB - read from the environment only.
    ai_api_key: str = ""

    # GitHub READ integration (Phase 4). Strictly read-only: the app never
    # writes to any repository. Same disabled-by-default pattern as ai_provider.
    github_provider: str = "disabled"  # disabled | github
    github_api_base: str = "https://api.github.com"
    # Fine-grained PAT with read-only contents/metadata scope. Never logged,
    # never stored in the DB - read from the environment only.
    github_token: str = ""


settings = Settings()
