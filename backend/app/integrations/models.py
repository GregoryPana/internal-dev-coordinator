"""Integration settings + persisted repo activity snapshots."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class IntegrationSetting(Base):
    """One row per integration provider ("github", later "openrouter", ...).
    encrypted_credential holds the Fernet ciphertext of the token/key -
    NEVER the plaintext, and no API ever returns it in any form."""

    __tablename__ = "integration_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    encrypted_credential: Mapped[str | None] = mapped_column(Text)
    config_json: Mapped[dict | None] = mapped_column(JSONB)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("people.id"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RepoSnapshot(Base):
    """Persisted result of one repo-signals fetch for one project - the
    storage behind active tracking. Append-only by convention; latest row
    per project is the current view. Deliberately does NOT touch
    Project.data_as_of - freshness stays human-evidence-driven until that
    semantic change is explicitly decided."""

    __tablename__ = "repo_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error: Mapped[str | None] = mapped_column(Text)
    data_json: Mapped[dict | None] = mapped_column(JSONB)
