"""Read-only audit API. No POST/PATCH/DELETE routes exist by design -
audit_events is append-only and written solely via app.audit.service.record().
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.audit.schemas import AuditEventPage
from app.authz import service as authz
from app.db import get_db
from app.registry import service as registry_service
from app.registry.models import Person
from app.vocab import AuditActionType, AuditObjectType

router = APIRouter(tags=["audit"])


@router.get("/api/audit/events", response_model=AuditEventPage)
def list_audit_events(
    action_type: AuditActionType | None = None,
    object_type: AuditObjectType | None = None,
    project_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> AuditEventPage:
    authz.require_audit_portfolio_read(user)
    return audit_service.list_events(
        db,
        project_id=project_id,
        action_type=action_type,
        object_type=object_type,
        limit=limit,
        offset=offset,
    )


@router.get("/api/projects/{project_id}/audit-events", response_model=AuditEventPage)
def list_project_audit_events(
    project_id: int,
    action_type: AuditActionType | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> AuditEventPage:
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    authz.require_read(db, user, project)
    return audit_service.list_events(
        db,
        project_id=project_id,
        action_type=action_type,
        limit=limit,
        offset=offset,
    )
