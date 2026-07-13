"""Starter-pack API: deterministic preview generation only (T7).

AI tailoring, StarterPack persistence, review workflow and zip export are
T8 - not built here.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.authz import service as authz
from app.db import get_db
from app.registry import service as registry_service
from app.registry.models import Person
from app.starterpack.schemas import IntakeForm, StarterPackPreview
from app.starterpack.service import build_preview
from app.vocab import AuditActionType, AuditObjectType

router = APIRouter(prefix="/api/projects/{project_id}/starter-pack", tags=["starter-pack"])


@router.post("/preview", response_model=StarterPackPreview)
def generate_preview(
    project_id: int,
    intake: IntakeForm,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> StarterPackPreview:
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    authz.require_update(db, user, project)

    files = build_preview(project, intake)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.STARTER_PACK_GENERATED,
        object_type=AuditObjectType.STARTER_PACK,
        object_id=None,
        project_id=project.id,
        metadata={"file_count": len(files), "deployment_target": intake.deployment_target},
    )
    db.commit()
    return StarterPackPreview(project_id=project.id, files=files)
