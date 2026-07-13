"""Core people/project models owned by the registry domain."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.vocab import (
    Classification,
    Priority,
    ProjectPhase,
    ProjectStatus,
    ProjectType,
    Role,
)


def _enum(e, name: str) -> Enum:
    """Native Postgres enum from a StrEnum, stored by value."""
    return Enum(e, name=name, values_callable=lambda x: [i.value for i in x])


# Shared type object: the 'role' Postgres enum is used by multiple columns
# (people.role_type, project_members.role) and must be created exactly once.
ROLE_ENUM = _enum(Role, "role")


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    role_type: Mapped[Role] = mapped_column(ROLE_ENUM)
    department: Mapped[str | None] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    business_purpose: Mapped[str | None] = mapped_column(Text)
    project_type: Mapped[ProjectType] = mapped_column(_enum(ProjectType, "project_type"))
    classification: Mapped[Classification] = mapped_column(_enum(Classification, "classification"))
    phase: Mapped[ProjectPhase] = mapped_column(_enum(ProjectPhase, "project_phase"))
    status: Mapped[ProjectStatus] = mapped_column(_enum(ProjectStatus, "project_status"))
    priority: Mapped[Priority] = mapped_column(_enum(Priority, "priority"))
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"))
    business_owner: Mapped[str | None] = mapped_column(String(200))
    current_next_action: Mapped[str | None] = mapped_column(Text)
    repo_url: Mapped[str | None] = mapped_column(String(500))
    environment_url: Mapped[str | None] = mapped_column(String(500))
    docs_url: Mapped[str | None] = mapped_column(String(500))
    tech_stack_summary: Mapped[str | None] = mapped_column(Text)
    # Freshness anchor: timestamp of the latest status event (FR-008/FR-023).
    data_as_of: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped[Person | None] = relationship()
    members: Mapped[list["ProjectMember"]] = relationship(back_populates="project")


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "person_id", name="uq_project_person"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), index=True)
    role: Mapped[Role] = mapped_column(ROLE_ENUM)

    project: Mapped[Project] = relationship(back_populates="members")
    person: Mapped[Person] = relationship()
