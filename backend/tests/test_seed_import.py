"""Tests for the one-shot seed import (T6): idempotency, validation, and
that it composes the existing status/docs_matrix services correctly.
Uses synthetic example data only - never the real pilot project content.
"""

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.docs_matrix.service import get_matrix
from app.registry.models import Person, Project
from app.seed_import.schemas import SeedFile
from app.seed_import.service import run_import
from app.vocab import ArtifactStatus, ArtifactType, Role

SYNTHETIC_FILE = {
    "people": [
        {"name": "Test Owner", "email": "owner@example.test", "role_type": "developer_project_owner"},
    ],
    "projects": [
        {
            "name": "Synthetic Pilot Project",
            "project_type": "prototype",
            "classification": "one-off",
            "phase": "pilot",
            "status": "active",
            "priority": "medium",
            "owner_email": "owner@example.test",
            "current_next_action": "Ship the pilot.",
            "status_events": [
                {
                    "event_date": "2026-06-01",
                    "summary": "Pilot kicked off.",
                    "author_email": "owner@example.test",
                    "completed_work": "Environment provisioned.",
                }
            ],
            "documentation_artifacts": [
                {
                    "artifact_type": "exit_md",
                    "status": "current",
                    "title": "EXIT.md",
                    "source_path": "EXIT.md",
                }
            ],
        }
    ],
}


def test_import_creates_person_project_status_event_and_doc_artifact(db: Session) -> None:
    data = SeedFile.model_validate(SYNTHETIC_FILE)
    summary = run_import(db, data)

    assert summary.people_created == 1
    assert summary.projects_created == 1
    assert summary.status_events_created == 1
    assert summary.doc_artifacts_upserted == 1

    project = db.scalar(select(Project).where(Project.slug == "synthetic-pilot-project"))
    assert project is not None
    assert project.current_next_action == "Ship the pilot."
    assert project.owner.email == "owner@example.test"
    assert project.data_as_of is not None  # freshness anchor set by the status event

    matrix = get_matrix(db, project)
    exit_md = next(e for e in matrix if e.artifact_type == ArtifactType.EXIT_MD)
    assert exit_md.status == ArtifactStatus.CURRENT
    assert exit_md.is_gap is False


def test_rerunning_same_file_does_not_duplicate_anything(db: Session) -> None:
    data = SeedFile.model_validate(SYNTHETIC_FILE)
    run_import(db, data)
    second = run_import(db, data)

    assert second.projects_created == 0
    assert second.projects_updated == 1
    assert second.status_events_created == 0
    assert second.status_events_skipped_duplicate == 1
    assert second.people_created == 0

    projects = list(db.scalars(select(Project).where(Project.slug == "synthetic-pilot-project")))
    assert len(projects) == 1


def test_rerun_with_new_status_event_adds_only_the_new_one(db: Session) -> None:
    data = SeedFile.model_validate(SYNTHETIC_FILE)
    run_import(db, data)

    updated = dict(SYNTHETIC_FILE)
    updated["projects"][0]["status_events"] = SYNTHETIC_FILE["projects"][0]["status_events"] + [
        {
            "event_date": "2026-06-15",
            "summary": "Pilot progressing well.",
            "author_email": "owner@example.test",
        }
    ]
    second = run_import(db, SeedFile.model_validate(updated))

    assert second.status_events_created == 1
    assert second.status_events_skipped_duplicate == 1


def test_unknown_owner_email_raises_clear_error(db: Session) -> None:
    bad = {
        "people": [],
        "projects": [
            {
                "name": "Orphan Owner Project",
                "project_type": "prototype",
                "classification": "one-off",
                "phase": "concept",
                "status": "active",
                "priority": "low",
                "owner_email": "nobody@example.test",
            }
        ],
    }
    with pytest.raises(ValueError, match="nobody@example.test"):
        run_import(db, SeedFile.model_validate(bad))


def test_invalid_enum_value_fails_schema_validation() -> None:
    bad = {
        "projects": [
            {
                "name": "Bad Phase Project",
                "project_type": "prototype",
                "classification": "one-off",
                "phase": "not-a-real-phase",
                "status": "active",
                "priority": "low",
            }
        ]
    }
    with pytest.raises(ValidationError):
        SeedFile.model_validate(bad)


def test_existing_person_is_not_recreated(db: Session, make_person) -> None:
    existing = make_person(Role.ADMIN, email="owner@example.test")
    db.commit()

    data = SeedFile.model_validate(SYNTHETIC_FILE)
    summary = run_import(db, data)

    assert summary.people_created == 0
    project = db.scalar(select(Project).where(Project.slug == "synthetic-pilot-project"))
    assert project.owner_id == existing.id
    # role_type from the pre-existing record is preserved, not overwritten by the seed file
    assert db.get(Person, existing.id).role_type == Role.ADMIN
