"""Status event API: create/list under a project. The main update primitive."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.authz import service as authz
from app.db import get_db
from app.registry import service as registry_service
from app.registry.models import Person
from app.status import service as status_service
from app.status.schemas import StatusEventCreate, StatusEventRead
from app.vocab import AuditActionType, AuditObjectType

router = APIRouter(prefix="/api/projects/{project_id}/status-events", tags=["status-events"])


def _get_project_or_404(db: Session, project_id: int):
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.get("", response_model=list[StatusEventRead])
def list_status_events(
    project_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> list[StatusEventRead]:
    project = _get_project_or_404(db, project_id)
    authz.require_read(db, user, project)
    events = status_service.list_status_events_for_project(db, project_id)
    return [StatusEventRead.model_validate(e) for e in events]


@router.post("", response_model=StatusEventRead, status_code=status.HTTP_201_CREATED)
def create_status_event(
    project_id: int,
    data: StatusEventCreate,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> StatusEventRead:
    project = _get_project_or_404(db, project_id)
    authz.require_update(db, user, project)
    event = status_service.create_status_event(db, project, user, data)
    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.STATUS_EVENT_CREATED,
        object_type=AuditObjectType.STATUS_EVENT,
        object_id=event.id,
        project_id=project.id,
        metadata={"event_date": data.event_date.isoformat()},
    )
    db.commit()
    db.refresh(event)
    return StatusEventRead.model_validate(event)
