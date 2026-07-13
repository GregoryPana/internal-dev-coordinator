"""Pydantic schemas for the starter-pack generator: deterministic
templates + intake form (T7, FR-013/FR-014/FR-016) plus AI tailoring,
persistence, review workflow and zip export (T8).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.vocab import HumanReviewStatus


class IntakeForm(BaseModel):
    """FR-013/FR-014: structured intake for a new project's starter pack.

    project_type/classification already live on Project and drive template
    selection directly; this form only captures what Project doesn't.
    """

    users: str = Field(min_length=1, description="Who will use this system.")
    workflow: str = Field(min_length=1, description="The core workflow being digitalised.")
    data_sensitivity: str = Field(min_length=1, description="What kind of data this handles, if any.")
    integrations: str | None = Field(default=None, description="Other systems this needs to talk to.")
    deployment_target: str = Field(min_length=1, description="Where this will run (e.g. internal VM).")
    notes: str | None = None


class GeneratedFile(BaseModel):
    path: str
    content: str


class StarterPackPreview(BaseModel):
    project_id: int
    files: list[GeneratedFile]


class StarterPackReviewerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class StarterPackRead(BaseModel):
    id: int
    project_id: int
    intake: IntakeForm
    files: list[GeneratedFile]
    status: HumanReviewStatus
    reviewer: StarterPackReviewerRead | None
    export_path: str | None
    created_at: datetime


class ReviewDecision(BaseModel):
    decision: Literal[HumanReviewStatus.REVIEWED, HumanReviewStatus.REJECTED]
