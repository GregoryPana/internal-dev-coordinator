"""AIInteraction: full logging for every AI run (FR-021, AGENTS.md AI
boundary). Created only for an actual attempted AI call - if the
provider is disabled, no AI run happens and no row is created (starter
packs still work deterministically; see app.ai.service).
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.registry.models import Project
from app.vocab import AIAudience, AITaskType, ErrorCategory, HumanReviewStatus, ValidationStatus


def _enum(e, name: str) -> Enum:
    return Enum(e, name=name, values_callable=lambda x: [i.value for i in x])


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    task_type: Mapped[AITaskType] = mapped_column(_enum(AITaskType, "ai_task_type"))
    audience: Mapped[AIAudience | None] = mapped_column(_enum(AIAudience, "ai_audience"))
    prompt_id: Mapped[str] = mapped_column(Text)
    prompt_version: Mapped[int] = mapped_column(Integer)
    source_ids_json: Mapped[dict] = mapped_column(JSONB)
    input_bundle_hash: Mapped[str] = mapped_column(Text)
    model_provider: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str | None] = mapped_column(Text)
    output_json: Mapped[dict | None] = mapped_column(JSONB)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_category: Mapped[ErrorCategory | None] = mapped_column(_enum(ErrorCategory, "error_category"))
    estimated_cost: Mapped[float | None] = mapped_column(Float)
    validation_status: Mapped[ValidationStatus] = mapped_column(_enum(ValidationStatus, "validation_status"))
    human_review_status: Mapped[HumanReviewStatus] = mapped_column(
        _enum(HumanReviewStatus, "human_review_status")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped[Project] = relationship()
