"""Pydantic schemas for status events (T4)."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class StatusEventAuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class StatusEventCreate(BaseModel):
    event_date: date
    summary: str = Field(min_length=1)
    completed_work: str | None = None
    next_actions: str | None = None
    blockers: str | None = None
    verification_notes: str | None = None


class StatusEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    author: StatusEventAuthorRead
    event_date: date
    summary: str
    completed_work: str | None
    next_actions: str | None
    blockers: str | None
    verification_notes: str | None
    created_at: datetime
