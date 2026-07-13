"""Input schema for the one-shot vault/CSV seed import (T6).

Strict: every enum field is validated against backend/app/vocab.py at
parse time, so a malformed or placeholder-only import file fails fast
with a clear error instead of writing partial/garbage rows.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.vocab import (
    ArtifactStatus,
    ArtifactType,
    Classification,
    Priority,
    ProjectPhase,
    ProjectStatus,
    ProjectType,
    Role,
)


class SeedPerson(BaseModel):
    name: str = Field(min_length=1)
    email: str
    role_type: Role
    department: str | None = None


class SeedStatusEvent(BaseModel):
    event_date: date
    summary: str = Field(min_length=1)
    author_email: str
    completed_work: str | None = None
    next_actions: str | None = None
    blockers: str | None = None
    verification_notes: str | None = None


class SeedDocumentationArtifact(BaseModel):
    artifact_type: ArtifactType
    status: ArtifactStatus
    title: str | None = None
    source_path: str | None = None
    owner_email: str | None = None
    last_reviewed_at: datetime | None = None
    notes: str | None = None


class SeedProject(BaseModel):
    slug: str | None = None
    name: str = Field(min_length=1)
    description: str | None = None
    business_purpose: str | None = None
    project_type: ProjectType
    classification: Classification
    phase: ProjectPhase
    status: ProjectStatus
    priority: Priority
    owner_email: str | None = None
    business_owner: str | None = None
    current_next_action: str | None = None
    repo_url: str | None = None
    environment_url: str | None = None
    docs_url: str | None = None
    tech_stack_summary: str | None = None
    status_events: list[SeedStatusEvent] = Field(default_factory=list)
    documentation_artifacts: list[SeedDocumentationArtifact] = Field(default_factory=list)


class SeedFile(BaseModel):
    """Top-level shape of a seed-import JSON file."""

    people: list[SeedPerson] = Field(default_factory=list)
    projects: list[SeedProject] = Field(min_length=1)
