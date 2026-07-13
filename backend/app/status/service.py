"""Status event business logic: create/list, and freshness recomputation.

Project.data_as_of is the freshness anchor (FR-008/FR-023): it is always
derived from the latest event_date across a project's status events, never
edited directly - see app.registry.schemas (ProjectUpdate has no data_as_of).
"""

from datetime import datetime, time, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.registry.models import Person, Project
from app.status.models import StatusEvent
from app.status.schemas import StatusEventCreate


def _as_datetime(d) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _recompute_data_as_of(db: Session, project: Project) -> None:
    latest = db.scalar(select(func.max(StatusEvent.event_date)).where(StatusEvent.project_id == project.id))
    project.data_as_of = _as_datetime(latest) if latest else None


def list_status_events_for_project(db: Session, project_id: int) -> list[StatusEvent]:
    stmt = (
        select(StatusEvent)
        .where(StatusEvent.project_id == project_id)
        .order_by(StatusEvent.event_date.desc(), StatusEvent.created_at.desc())
    )
    return list(db.scalars(stmt))


def create_status_event(
    db: Session, project: Project, author: Person, data: StatusEventCreate
) -> StatusEvent:
    event = StatusEvent(project_id=project.id, author_id=author.id, **data.model_dump())
    db.add(event)
    db.flush()
    _recompute_data_as_of(db, project)
    db.flush()
    return event
