"""Project registry API: portfolio list, project profile, create/update.

All permission decisions go through app.authz; every mutation is audited.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.authz import service as authz
from app.db import get_db
from app.registry import service as registry_service
from app.registry.models import Person
from app.registry.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.vocab import AuditActionType, AuditObjectType

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _get_project_or_404(db: Session, project_id: int):
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


def _latest_pushes(db: Session, project_ids: list[int]) -> dict[int, "datetime"]:
    """project_id -> pushed_at from the newest successful repo snapshot per
    project. One query; display-only enrichment."""
    if not project_ids:
        return {}
    from datetime import datetime

    from sqlalchemy import select

    from app.integrations.models import RepoSnapshot

    rows = db.execute(
        select(RepoSnapshot.project_id, RepoSnapshot.data_json)
        .where(RepoSnapshot.project_id.in_(project_ids), RepoSnapshot.success.is_(True))
        .order_by(RepoSnapshot.project_id, RepoSnapshot.id.desc())
        .distinct(RepoSnapshot.project_id)
    ).all()
    result = {}
    for project_id, data in rows:
        pushed = (data or {}).get("pushed_at")
        if pushed:
            result[project_id] = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
    return result


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> list[ProjectRead]:
    projects = registry_service.list_projects_for_user(db, user)
    pushes = _latest_pushes(db, [p.id for p in projects])
    return [
        registry_service.to_read(p).model_copy(update={"repo_last_push": pushes.get(p.id)})
        for p in projects
    ]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> ProjectRead:
    authz.require_create(user)
    project = registry_service.create_project(db, data)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.PROJECT_CREATED,
        object_type=AuditObjectType.PROJECT,
        object_id=project.id,
        project_id=project.id,
        metadata={"slug": project.slug, "name": project.name},
    )
    db.commit()
    db.refresh(project)
    return registry_service.to_read(project)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> ProjectRead:
    project = _get_project_or_404(db, project_id)
    authz.require_read(db, user, project)
    return registry_service.to_read(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> ProjectRead:
    project = _get_project_or_404(db, project_id)
    authz.require_evidence_write(db, user, project)
    changed_fields = sorted(data.model_dump(exclude_unset=True).keys())
    project = registry_service.update_project(db, project, data)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.PROJECT_UPDATED,
        object_type=AuditObjectType.PROJECT,
        object_id=project.id,
        project_id=project.id,
        metadata={"fields": changed_fields},
    )
    db.commit()
    db.refresh(project)
    return registry_service.to_read(project)
