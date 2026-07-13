"""Audit recording - the only write path to audit_events. Append-only."""

from sqlalchemy.orm import Session

from app.audit.models import AuditEvent
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
