"""Status event model - the main update primitive (FR-008).

Every status event moves Project.data_as_of forward (see app.status.service);
data_as_of is the freshness anchor shown on the dashboard and profile.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.registry.models import Person


class StatusEvent(Base):
    __tablename__ = "status_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("people.id"))
    event_date: Mapped[date] = mapped_column(Date)
    summary: Mapped[str] = mapped_column(Text)
    completed_work: Mapped[str | None] = mapped_column(Text)
    next_actions: Mapped[str | None] = mapped_column(Text)
    blockers: Mapped[str | None] = mapped_column(Text)
    verification_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    author: Mapped[Person] = relationship()
