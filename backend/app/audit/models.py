"""Append-only audit event model.

The app layer exposes ONLY record() (see app.audit.service). There must
never be an update or delete path for audit_events.
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.vocab import AuditActionType, AuditObjectType


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True)
    action_type: Mapped[AuditActionType] = mapped_column(
        Enum(AuditActionType, name="audit_action_type", values_callable=lambda x: [i.value for i in x])
    )
    object_type: Mapped[AuditObjectType] = mapped_column(
        Enum(AuditObjectType, name="audit_object_type", values_callable=lambda x: [i.value for i in x])
    )
    object_id: Mapped[int | None] = mapped_column()
    metadata_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
