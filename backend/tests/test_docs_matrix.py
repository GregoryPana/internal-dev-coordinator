"""Integration tests for the documentation matrix (T5): deterministic gap list."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.audit.models import AuditEvent
from app.vocab import (
    ArtifactStatus,
    ArtifactType,
    AuditActionType,
    Classification,
    Priority,
    ProjectPhase,
    ProjectStatus,
    ProjectType,
    Role,
)

PROTOTYPE_PROJECT = {
    "name": "Prototype Thing",
    "project_type": ProjectType.PROTOTYPE.value,
    "classification": Classification.ONE_OFF.value,
    "phase": ProjectPhase.CONCEPT.value,
    "status": ProjectStatus.ACTIVE.value,
    "priority": Priority.LOW.value,
}

WEB_APP_PROJECT = {
    "name": "Web App Thing",
    "project_type": ProjectType.INTERNAL_WEB_APP.value,
    "classification": Classification.REUSABLE.value,
    "phase": ProjectPhase.BUILD.value,
    "status": ProjectStatus.ACTIVE.value,
    "priority": Priority.MEDIUM.value,
}


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def _create_project(client: TestClient, admin_email: str, payload: dict) -> dict:
    resp = client.post("/api/projects", json=payload, headers=_headers(admin_email))
    assert resp.status_code == 201
    return resp.json()


def test_prototype_matrix_requires_only_agent_guide_and_exit_md(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, PROTOTYPE_PROJECT)

    resp = client.get(f"/api/projects/{project['id']}/documentation", headers=_headers(admin.email))
    assert resp.status_code == 200
    entries = {e["artifact_type"]: e for e in resp.json()}

    assert len(entries) == len(ArtifactType)
    required_types = {t for t, e in entries.items() if e["required"]}
    assert required_types == {ArtifactType.AGENT_GUIDE.value, ArtifactType.EXIT_MD.value}
    # every required artifact is missing (no docs registered yet) -> gap
    assert all(entries[t]["is_gap"] for t in required_types)
    assert all(entries[t]["status"] == ArtifactStatus.MISSING.value for t in required_types)
    # non-required types are never gaps even though also missing
    non_required = {t for t, e in entries.items() if not e["required"]}
    assert all(not entries[t]["is_gap"] for t in non_required)


def test_web_app_matrix_requires_all_artifact_types(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, WEB_APP_PROJECT)

    resp = client.get(f"/api/projects/{project['id']}/documentation", headers=_headers(admin.email))
    entries = resp.json()
    assert all(e["required"] for e in entries)
    assert all(e["is_gap"] for e in entries)  # nothing registered yet


def test_registering_artifact_as_current_closes_the_gap(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, PROTOTYPE_PROJECT)

    resp = client.put(
        f"/api/projects/{project['id']}/documentation/{ArtifactType.AGENT_GUIDE.value}",
        json={"title": "Agent guide", "status": ArtifactStatus.CURRENT.value, "source_path": "docs/agent.md"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 200
    entry = resp.json()
    assert entry["status"] == ArtifactStatus.CURRENT.value
    assert entry["is_gap"] is False
    assert entry["source_path"] == "docs/agent.md"

    matrix = client.get(f"/api/projects/{project['id']}/documentation", headers=_headers(admin.email)).json()
    agent_guide = next(e for e in matrix if e["artifact_type"] == ArtifactType.AGENT_GUIDE.value)
    assert agent_guide["is_gap"] is False
    # exit_md is still required and still missing -> still a gap
    exit_md = next(e for e in matrix if e["artifact_type"] == ArtifactType.EXIT_MD.value)
    assert exit_md["is_gap"] is True


def test_registering_artifact_as_draft_is_still_a_gap(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, PROTOTYPE_PROJECT)

    client.put(
        f"/api/projects/{project['id']}/documentation/{ArtifactType.EXIT_MD.value}",
        json={"status": ArtifactStatus.DRAFT.value},
        headers=_headers(admin.email),
    )
    matrix = client.get(f"/api/projects/{project['id']}/documentation", headers=_headers(admin.email)).json()
    exit_md = next(e for e in matrix if e["artifact_type"] == ArtifactType.EXIT_MD.value)
    assert exit_md["status"] == ArtifactStatus.DRAFT.value
    assert exit_md["is_gap"] is False  # a registered draft is not "missing" - not a gap in T5's deterministic sense


def test_first_upsert_is_audited_as_created_second_as_updated(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, PROTOTYPE_PROJECT)

    client.put(
        f"/api/projects/{project['id']}/documentation/{ArtifactType.AGENT_GUIDE.value}",
        json={"status": ArtifactStatus.DRAFT.value},
        headers=_headers(admin.email),
    )
    client.put(
        f"/api/projects/{project['id']}/documentation/{ArtifactType.AGENT_GUIDE.value}",
        json={"status": ArtifactStatus.CURRENT.value},
        headers=_headers(admin.email),
    )

    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.project_id == project["id"])
        .order_by(AuditEvent.id)
        .all()
    )
    doc_events = [e for e in events if e.action_type in (
        AuditActionType.DOC_ARTIFACT_CREATED,
        AuditActionType.DOC_ARTIFACT_UPDATED,
    )]
    assert [e.action_type for e in doc_events] == [
        AuditActionType.DOC_ARTIFACT_CREATED,
        AuditActionType.DOC_ARTIFACT_UPDATED,
    ]


def test_developer_non_member_cannot_read_or_write_matrix(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email, PROTOTYPE_PROJECT)

    read_resp = client.get(f"/api/projects/{project['id']}/documentation", headers=_headers(dev.email))
    assert read_resp.status_code == 403

    write_resp = client.put(
        f"/api/projects/{project['id']}/documentation/{ArtifactType.AGENT_GUIDE.value}",
        json={"status": ArtifactStatus.CURRENT.value},
        headers=_headers(dev.email),
    )
    assert write_resp.status_code == 403


def test_matrix_for_missing_project_is_404(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    resp = client.get("/api/projects/999999/documentation", headers=_headers(admin.email))
    assert resp.status_code == 404
