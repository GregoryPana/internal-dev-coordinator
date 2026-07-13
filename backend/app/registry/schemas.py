"""Pydantic schemas for the registry domain (Project CRUD, T3)."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.vocab import Classification, Priority, ProjectPhase, ProjectStatus, ProjectType


class ProjectOwnerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    business_purpose: str | None = None
    project_type: ProjectType
    classification: Classification
    phase: ProjectPhase
    status: ProjectStatus
    priority: Priority
    owner_id: int | None = None
    business_owner: str | None = Field(default=None, max_length=200)
    current_next_action: str | None = None
    repo_url: str | None = Field(default=None, max_length=500)
    environment_url: str | None = Field(default=None, max_length=500)
    docs_url: str | None = Field(default=None, max_length=500)
    tech_stack_summary: str | None = None
    date_commenced: date | None = None
    expected_finish_date: date | None = None
    percent_complete: int | None = Field(default=None, ge=0, le=100)
    uses_process_automation: bool = False
    uses_ai: bool = False


class ProjectCreate(ProjectBase):
    # Optional: derived from name via slugify() when omitted.
    slug: str | None = Field(default=None, max_length=120)


class ProjectUpdate(BaseModel):
    """All fields optional - PATCH semantics. Slug is immutable after creation."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    business_purpose: str | None = None
    project_type: ProjectType | None = None
    classification: Classification | None = None
    phase: ProjectPhase | None = None
    status: ProjectStatus | None = None
    priority: Priority | None = None
    owner_id: int | None = None
    business_owner: str | None = Field(default=None, max_length=200)
    current_next_action: str | None = None
    repo_url: str | None = Field(default=None, max_length=500)
    environment_url: str | None = Field(default=None, max_length=500)
    docs_url: str | None = Field(default=None, max_length=500)
    tech_stack_summary: str | None = None
    date_commenced: date | None = None
    expected_finish_date: date | None = None
    percent_complete: int | None = Field(default=None, ge=0, le=100)
    uses_process_automation: bool | None = None
    uses_ai: bool | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    owner: ProjectOwnerRead | None
    data_as_of: datetime | None
    is_stale: bool
    created_at: datetime
    updated_at: datetime
