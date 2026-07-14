"""AI service-account access: member agents read state and record evidence
but can never pass a human-review gate (FR-022)."""

import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.authz.provision_agent import provision
from app.registry.models import ProjectMember
from app.vocab import Classification, Priority, ProjectPhase, ProjectStatus, ProjectType, Role


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def _create_project(client: TestClient, admin_email: str, **overrides) -> dict:
    payload = {
        "name": "Agent Access Project",
        "project_type": ProjectType.OPERATIONAL_TOOL.value,
        "classification": Classification.REUSABLE.value,
        "phase": ProjectPhase.ONGOING_DEVELOPMENT.value,
        "status": ProjectStatus.ACTIVE.value,
        "priority": Priority.MEDIUM.value,
        **overrides,
    }
    resp = client.post("/api/projects", json=payload, headers=_headers(admin_email))
    assert resp.status_code == 201
    return resp.json()


def _make_agent(db: Session, make_person, project_id: int):
    agent = make_person(Role.AI_SERVICE_ACCOUNT)
    db.add(ProjectMember(project_id=project_id, person_id=agent.id, role=Role.AI_SERVICE_ACCOUNT))
    db.flush()
    return agent


def test_member_agent_reads_and_records_evidence(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    agent = _make_agent(db, make_person, project["id"])
    db.commit()

    # Read project state.
    resp = client.get(f"/api/projects/{project['id']}", headers=_headers(agent.email))
    assert resp.status_code == 200

    # Post a status event - the primary agent update path.
    resp = client.post(
        f"/api/projects/{project['id']}/status-events",
        json={
            "event_date": "2026-07-14",
            "summary": "Vault sync: register entry updated.",
            "verification_notes": "Source: Hermes vault register.",
        },
        headers=_headers(agent.email),
    )
    assert resp.status_code == 201
    assert resp.json()["author"]["email"] == agent.email

    # Update registry fields.
    resp = client.patch(
        f"/api/projects/{project['id']}",
        json={"percent_complete": 40, "current_next_action": "Next per vault."},
        headers=_headers(agent.email),
    )
    assert resp.status_code == 200
    assert resp.json()["percent_complete"] == 40

    # Upsert a documentation artifact.
    resp = client.put(
        f"/api/projects/{project['id']}/documentation/exit_md",
        json={
            "title": "EXIT.md",
            "status": "draft",
            "source_path": "EXIT.md",
            "owner_id": None,
            "last_reviewed_at": None,
            "notes": "Synced from vault.",
        },
        headers=_headers(agent.email),
    )
    assert resp.status_code == 200


def test_non_member_agent_gets_403(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    outsider_agent = make_person(Role.AI_SERVICE_ACCOUNT)
    db.commit()

    assert (
        client.get(f"/api/projects/{project['id']}", headers=_headers(outsider_agent.email)).status_code
        == 403
    )
    resp = client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": "2026-07-14", "summary": "Should not land."},
        headers=_headers(outsider_agent.email),
    )
    assert resp.status_code == 403


def test_agent_cannot_pass_human_review_gates(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    """FR-022: even a member agent must never review/approve AI output."""
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    agent = _make_agent(db, make_person, project["id"])
    db.commit()

    # Generate a summary as admin with a fake provider, then try to review as the agent.
    from app.config import settings as app_settings
    from app.ai.provider import ProviderResult

    class FakeProvider:
        def complete(self, prompt: str) -> ProviderResult:
            return ProviderResult(
                text=json.dumps(
                    {
                        "summary": "Test.",
                        "assumptions": [],
                        "gaps": [],
                        "recommended_next_actions": [],
                        "requires_human_review": True,
                        "confidence": 0.5,
                    }
                ),
                model_name="fake",
                input_tokens=1,
                output_tokens=1,
            )

    monkeypatch.setattr(app_settings, "ai_provider", "fake")
    monkeypatch.setattr("app.ai.summary_service.get_provider", lambda: FakeProvider())
    summary = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    ).json()

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summaries/{summary['id']}/review",
        json={"decision": "reviewed"},
        headers=_headers(agent.email),
    )
    assert resp.status_code == 403

    # Starter-pack generation/review are likewise human-gated.
    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json={
            "users": "x", "workflow": "x", "data_sensitivity": "x",
            "integrations": "", "deployment_target": "x", "notes": "",
        },
        headers=_headers(agent.email),
    )
    assert resp.status_code == 403


def test_provision_agent_is_idempotent(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, name="Provision Target")

    person, added_first = provision(db, email="test-agent@cws.local", name="Test Agent")
    assert person.role_type == Role.AI_SERVICE_ACCOUNT
    assert added_first >= 1  # at least the project created above

    person2, added_second = provision(db, email="test-agent@cws.local", name="Test Agent")
    assert person2.id == person.id
    assert added_second == 0  # nothing new to add

    # The agent can now read the project it was given membership to.
    resp = client.get(f"/api/projects/{project['id']}", headers=_headers(person.email))
    assert resp.status_code == 200
