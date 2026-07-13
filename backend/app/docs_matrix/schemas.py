"""Pydantic schemas for the documentation matrix (T5)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.vocab import ArtifactStatus, ArtifactType


class DocArtifactOwnerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class DocumentationArtifactUpsert(BaseModel):
    title: str | None = None
    status: ArtifactStatus
    source_path: str | None = None
    owner_id: int | None = None
    last_reviewed_at: datetime | None = None
    notes: str | None = None


class DocumentationMatrixEntry(BaseModel):
    """One row of the deterministic documentation matrix for a project:
    the required-doc profile joined with the project's current artifact
    record, if any exists."""

    artifact_type: ArtifactType
    required: bool
    status: ArtifactStatus
    is_gap: bool
    title: str | None
    source_path: str | None
    owner: DocArtifactOwnerRead | None
    last_reviewed_at: datetime | None
    staleness_checked_at: datetime | None
    notes: str | None
