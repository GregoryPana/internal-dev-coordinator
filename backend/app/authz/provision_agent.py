"""Provision (or refresh) an AI service-account agent.

Creates/updates a Person with role ai_service_account and adds it as a
member of every current project so it can read state and record evidence
(status events, doc artifacts, registry field updates). It can NEVER pass
a human-review gate - can_update_project excludes the role by design.

Usage (from backend/):
    python -m app.authz.provision_agent --email hermes@cws.local --name "Hermes (AI agent)"

Re-running is idempotent and picks up projects created since the last run.
Run it again (or add a membership row) whenever a new project should be
visible to the agent.
"""

import argparse

from sqlalchemy import select

from app.audit import service as audit_service
from app.db import SessionLocal
from app.registry.models import Person, Project, ProjectMember
from app.vocab import AuditActionType, AuditObjectType, Role


def provision(db, *, email: str, name: str) -> tuple[Person, int]:
    email = email.strip().lower()
    person = db.scalar(select(Person).where(Person.email == email))
    if person is None:
        person = Person(name=name, email=email, role_type=Role.AI_SERVICE_ACCOUNT, active=True)
        db.add(person)
        db.flush()
    else:
        person.name = name
        person.role_type = Role.AI_SERVICE_ACCOUNT
        person.active = True
        db.flush()

    added = 0
    for project in db.scalars(select(Project).order_by(Project.id)):
        existing = db.scalar(
            select(ProjectMember.id).where(
                ProjectMember.project_id == project.id, ProjectMember.person_id == person.id
            )
        )
        if existing is not None:
            continue
        db.add(ProjectMember(project_id=project.id, person_id=person.id, role=Role.AI_SERVICE_ACCOUNT))
        db.flush()
        audit_service.record(
            db,
            actor_id=person.id,
            action_type=AuditActionType.MEMBER_ADDED,
            object_type=AuditObjectType.PROJECT_MEMBER,
            project_id=project.id,
            metadata={"person_email": person.email, "role": Role.AI_SERVICE_ACCOUNT.value, "via": "provision_agent"},
        )
        added += 1
    return person, added


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="AI service account")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        person, added = provision(db, email=args.email, name=args.name)
        db.commit()
        print(f"Agent '{person.name}' <{person.email}> ready (id={person.id}); {added} project membership(s) added.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
