"""Persisted starter pack (T8). Generation is deterministic-first (T7);
this table exists so a generated pack can be reviewed and exported. AI
tailoring, when a provider is configured, augments generated_files_json
before it's stored here - see app.ai.service.
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.registry.models import Person, Project
from app.vocab import HumanReviewStatus


def _enum(e, name: str) -> Enum:
    return Enum(e, name=name, values_callable=lambda x: [i.value for i in x])


class StarterPack(Base):
    __tablename__ = "starter_packs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    intake_json: Mapped[dict] = mapped_column(JSONB)
    generated_files_json: Mapped[dict] = mapped_column(JSONB)
    export_path: Mapped[str | None] = mapped_column(Text)
    status: Mapped[HumanReviewStatus] = mapped_column(_enum(HumanReviewStatus, "human_review_status"))
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("people.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship()
    reviewer: Mapped[Person | None] = relationship()
