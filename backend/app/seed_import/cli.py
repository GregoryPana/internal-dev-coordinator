"""One-shot seed-import command.

Usage (from backend/, with the venv active and the DB migrated):

    python -m app.seed_import.cli --file path/to/pilot_projects.json

See app/seed_import/templates/pilot_projects.template.json and its
README for the exact file shape and field meanings.
"""

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import select

from app.audit import service as audit_service
from app.config import settings
from app.db import SessionLocal
from app.registry.models import Person
from app.seed_import.schemas import SeedFile
from app.seed_import.service import run_import
from app.vocab import AuditActionType, AuditObjectType


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path, help="Path to a seed-import JSON file.")
    parser.add_argument(
        "--actor-email",
        default=settings.dev_default_user_email,
        help="Email of the Person recorded as the audit actor (must already exist). "
        "Defaults to the bootstrap admin.",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1

    try:
        raw = json.loads(args.file.read_text(encoding="utf-8"))
        data = SeedFile.model_validate(raw)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"error: invalid seed file: {e}", file=sys.stderr)
        return 1

    db = SessionLocal()
    try:
        actor = db.scalar(select(Person).where(Person.email == args.actor_email))
        if actor is None:
            print(f"error: no Person with email '{args.actor_email}' - run migrations first.", file=sys.stderr)
            return 1

        summary = run_import(db, data)
        for project_id in summary.project_ids:
            audit_service.record(
                db,
                actor_id=actor.id,
                action_type=AuditActionType.SEED_IMPORT_RUN,
                object_type=AuditObjectType.PROJECT,
                object_id=project_id,
                project_id=project_id,
                metadata={"source_file": str(args.file)},
            )
        db.commit()
    except ValueError as e:
        db.rollback()
        print(f"error: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()

    print(
        "Seed import complete: "
        f"{summary.people_created} people created, "
        f"{summary.projects_created} projects created, "
        f"{summary.projects_updated} projects updated, "
        f"{summary.status_events_created} status events created "
        f"({summary.status_events_skipped_duplicate} duplicates skipped), "
        f"{summary.doc_artifacts_upserted} documentation artifacts upserted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
