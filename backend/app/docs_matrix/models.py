"""Documentation matrix models: required-doc profiles and per-project
documentation artifacts. Gap computation is deterministic (app.docs_matrix
.service) - no AI is involved in T5.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.registry.models import Person, Project
from app.vocab import ArtifactStatus, ArtifactType, ProjectType


def _enum(e, name: str) -> Enum:
    """Native Postgres enum from a StrEnum, stored by value."""
    return Enum(e, name=name, values_callable=lambda x: [i.value for i in x])


class RequiredDocProfile(Base):
    """Which artifact types are required for a given project_type.

    Seeded via migration from vocab.REQUIRED_DOC_PROFILES (the vocab law);
    kept as its own table (rather than read from vocab.py at request time)
    so each pairing can carry its own notes and be inspected/edited without
    a code change.
    """

    __tablename__ = "required_doc_profiles"
    __table_args__ = (UniqueConstraint("project_type", "artifact_type", name="uq_doc_profile_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_type: Mapped[ProjectType] = mapped_column(_enum(ProjectType, "project_type"))
    artifact_type: Mapped[ArtifactType] = mapped_column(_enum(ArtifactType, "artifact_type"))
    required: Mapped[bool] = mapped_column(Boolean)
    notes: Mapped[str | None] = mapped_column(Text)


class DocumentationArtifact(Base):
    """One artifact_type's current state for one project."""

    __tablename__ = "documentation_artifacts"
    __table_args__ = (UniqueConstraint("project_id", "artifact_type", name="uq_doc_artifact_project_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    artifact_type: Mapped[ArtifactType] = mapped_column(_enum(ArtifactType, "artifact_type"))
    title: Mapped[str | None] = mapped_column(Text)
    required: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[ArtifactStatus] = mapped_column(_enum(ArtifactStatus, "artifact_status"))
    source_path: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"))
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    staleness_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship()
    owner: Mapped[Person | None] = relationship()
