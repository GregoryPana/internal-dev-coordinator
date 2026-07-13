"""One-shot vault/CSV seed import (T6): pilot projects become the AI golden
set (T9/T10), so this import is deliberately safe to re-run as the source
export gets corrected - it upserts by natural key (email/slug/artifact_type)
rather than blindly inserting, but it never fabricates data itself; every
field must come from the caller's SeedFile.
"""

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.docs_matrix.schemas import DocumentationArtifactUpsert
from app.docs_matrix.service import upsert_artifact
from app.registry.models import Person, Project
from app.registry.service import slugify, unique_slug
from app.seed_import.schemas import SeedFile, SeedPerson, SeedProject
from app.status.models import StatusEvent
from app.status.schemas import StatusEventCreate
from app.status.service import create_status_event


@dataclass
class ImportSummary:
    people_created: int = 0
    projects_created: int = 0
    projects_updated: int = 0
    status_events_created: int = 0
    status_events_skipped_duplicate: int = 0
    doc_artifacts_upserted: int = 0
    project_ids: list[int] = field(default_factory=list)


def _upsert_person(db: Session, data: SeedPerson) -> Person:
    person = db.scalar(select(Person).where(Person.email == data.email))
    if person is None:
        person = Person(
            name=data.name, email=data.email, role_type=data.role_type, department=data.department, active=True
        )
        db.add(person)
        db.flush()
    return person


def _get_person_by_email(db: Session, email: str | None) -> Person | None:
    if email is None:
        return None
    person = db.scalar(select(Person).where(Person.email == email))
    if person is None:
        raise ValueError(f"No person record for email '{email}' - add them to the seed file's 'people' list.")
    return person


def _import_project(db: Session, data: SeedProject, summary: ImportSummary) -> Project:
    # Look up by the natural (unsuffixed) slug first, so re-running the same
    # import file updates the same project instead of creating a duplicate
    # with a "-2" suffix - unique_slug() is only used for a genuinely new slug.
    base_slug = slugify(data.slug or data.name)
    project = db.scalar(select(Project).where(Project.slug == base_slug))
    owner = _get_person_by_email(db, data.owner_email)

    fields = data.model_dump(exclude={"slug", "owner_email", "status_events", "documentation_artifacts"})
    if project is None:
        slug = unique_slug(db, base_slug)
        project = Project(slug=slug, owner_id=owner.id if owner else None, **fields)
        db.add(project)
        db.flush()
        summary.projects_created += 1
    else:
        for name, value in fields.items():
            setattr(project, name, value)
        project.owner_id = owner.id if owner else project.owner_id
        db.flush()
        summary.projects_updated += 1

    summary.project_ids.append(project.id)

    for event_data in data.status_events:
        author = _get_person_by_email(db, event_data.author_email)
        existing = db.scalar(
            select(StatusEvent.id).where(
                StatusEvent.project_id == project.id,
                StatusEvent.event_date == event_data.event_date,
                StatusEvent.summary == event_data.summary,
            )
        )
        if existing is not None:
            summary.status_events_skipped_duplicate += 1
            continue
        create_status_event(
            db,
            project,
            author,
            StatusEventCreate(
                event_date=event_data.event_date,
                summary=event_data.summary,
                completed_work=event_data.completed_work,
                next_actions=event_data.next_actions,
                blockers=event_data.blockers,
                verification_notes=event_data.verification_notes,
            ),
        )
        summary.status_events_created += 1

    for artifact_data in data.documentation_artifacts:
        owner_person = _get_person_by_email(db, artifact_data.owner_email)
        upsert_artifact(
            db,
            project,
            artifact_data.artifact_type,
            DocumentationArtifactUpsert(
                title=artifact_data.title,
                status=artifact_data.status,
                source_path=artifact_data.source_path,
                owner_id=owner_person.id if owner_person else None,
                last_reviewed_at=artifact_data.last_reviewed_at,
                notes=artifact_data.notes,
            ),
        )
        summary.doc_artifacts_upserted += 1

    return project


def run_import(db: Session, data: SeedFile) -> ImportSummary:
    summary = ImportSummary()
    for person_data in data.people:
        before = db.scalar(select(Person.id).where(Person.email == person_data.email))
        _upsert_person(db, person_data)
        if before is None:
            summary.people_created += 1

    for project_data in data.projects:
        _import_project(db, project_data, summary)

    return summary
