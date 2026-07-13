"""Read-only audit schemas. There is deliberately no write schema -
app.audit.service.record() is the only write path."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.vocab import AuditActionType, AuditObjectType


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    actor_name: str | None
    actor_email: str | None
    project_id: int | None
    action_type: AuditActionType
    object_type: AuditObjectType
    object_id: int | None
    metadata_json: dict | None
    created_at: datetime


class AuditEventPage(BaseModel):
    items: list[AuditEventRead]
    total: int
    limit: int
    offset: int
