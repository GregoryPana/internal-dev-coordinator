"""Registry business logic: project CRUD, slug handling, freshness, scoping.

No inline permission checks here - callers (the router) apply app.authz
before invoking these functions. Every mutation is audited by the router.
"""

import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.registry.models import Person, Project, ProjectMember
from app.registry.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.vocab import Role

_SLUG_RE = re.compile(r"[^a-z0-9]+")

# Roles that may see every project on the portfolio dashboard/list.
_PORTFOLIO_READ_ROLES = {Role.ADMIN, Role.MANAGER, Role.AUDITOR}


def slugify(name: str) -> str:
    slug = _SLUG_RE.sub("-", name.strip().lower()).strip("-")
    return slug or "project"


def unique_slug(db: Session, base_slug: str) -> str:
    slug = base_slug
    suffix = 2
    while db.scalar(select(Project.id).where(Project.slug == slug)) is not None:
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


def is_stale(data_as_of: datetime | None) -> bool:
    if data_as_of is None:
        return True
    now = datetime.now(timezone.utc)
    age = now - (data_as_of if data_as_of.tzinfo else data_as_of.replace(tzinfo=timezone.utc))
    return age.days > settings.freshness_threshold_days


def to_read(project: Project) -> ProjectRead:
    return ProjectRead.model_validate(
        {**project.__dict__, "is_stale": is_stale(project.data_as_of), "owner": project.owner}
    )


def list_projects_for_user(db: Session, user: Person) -> list[Project]:
    stmt = select(Project).order_by(Project.name)
    if user.role_type in _PORTFOLIO_READ_ROLES:
        return list(db.scalars(stmt))
    # Scoped roles (developer_project_owner, trainee, ai_service_account): owned or member-of only.
    member_project_ids = select(ProjectMember.project_id).where(ProjectMember.person_id == user.id)
    stmt = stmt.where((Project.owner_id == user.id) | (Project.id.in_(member_project_ids)))
    return list(db.scalars(stmt))


def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def create_project(db: Session, data: ProjectCreate) -> Project:
    base_slug = slugify(data.slug or data.name)
    slug = unique_slug(db, base_slug)
    project = Project(slug=slug, **data.model_dump(exclude={"slug"}))
    db.add(project)
    db.flush()
    return project


def update_project(db: Session, project: Project, data: ProjectUpdate) -> Project:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.flush()
    return project
