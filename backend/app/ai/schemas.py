"""Pydantic schemas for the AI project-summary task (T9, FR-018/FR-021)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.vocab import AIAudience, ErrorCategory, HumanReviewStatus, ValidationStatus


class GenerateSummaryRequest(BaseModel):
    audience: AIAudience


class SummaryOutput(BaseModel):
    """The structured schema the model must return (architecture spec 11.4).
    Validated strictly - anything that doesn't parse into this shape is a
    failed_schema run, not a best-effort guess at what the model meant."""

    summary: str = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommended_next_actions: list[str] = Field(default_factory=list)
    requires_human_review: bool
    confidence: float = Field(ge=0.0, le=1.0)


class AIInteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    task_type: str
    audience: AIAudience | None
    prompt_id: str
    prompt_version: int
    source_ids_json: dict
    model_provider: str
    model_name: str
    output_json: dict | None
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: int | None
    error_category: ErrorCategory | None
    validation_status: ValidationStatus
    human_review_status: HumanReviewStatus
    created_at: datetime


class ReviewDecision(BaseModel):
    decision: Literal[HumanReviewStatus.REVIEWED, HumanReviewStatus.REJECTED]
