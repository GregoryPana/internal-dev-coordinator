"""Audit recording and read queries. record() is the only write path to
audit_events - append-only, no update or delete ever."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit.models import AuditEvent
from app.audit.schemas import AuditEventPage, AuditEventRead
from app.registry.models import Person
from app.vocab import AuditActionType, AuditObjectType


def record(
    db: Session,
    *,
    actor_id: int | None,
    action_type: AuditActionType,
    object_type: AuditObjectType,
    object_id: int | None = None,
    project_id: int | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        actor_id=actor_id,
        project_id=project_id,
        action_type=action_type,
        object_type=object_type,
        object_id=object_id,
        metadata_json=metadata,
    )
    db.add(event)
    db.flush()
    return event


def list_events(
    db: Session,
    *,
    project_id: int | None = None,
    action_type: AuditActionType | None = None,
    object_type: AuditObjectType | None = None,
    limit: int = 50,
    offset: int = 0,
) -> AuditEventPage:
    """Newest-first page of audit events. Caller is responsible for authz
    (project read for project-scoped calls, audit-portfolio otherwise)."""
    conditions = []
    if project_id is not None:
        conditions.append(AuditEvent.project_id == project_id)
    if action_type is not None:
        conditions.append(AuditEvent.action_type == action_type)
    if object_type is not None:
        conditions.append(AuditEvent.object_type == object_type)

    total = db.scalar(select(func.count()).select_from(AuditEvent).where(*conditions)) or 0
    rows = db.execute(
        select(AuditEvent, Person.name, Person.email)
        .outerjoin(Person, AuditEvent.actor_id == Person.id)
        .where(*conditions)
        .order_by(AuditEvent.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    items = [
        AuditEventRead(
            id=event.id,
            actor_id=event.actor_id,
            actor_name=actor_name,
            actor_email=actor_email,
            project_id=event.project_id,
            action_type=event.action_type,
            object_type=event.object_type,
            object_id=event.object_id,
            metadata_json=event.metadata_json,
            created_at=event.created_at,
        )
        for event, actor_name, actor_email in rows
    ]
    return AuditEventPage(items=items, total=total, limit=limit, offset=offset)
