"""Integration tests for project CRUD (T3): scoping, slugs, audit trail."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.audit.models import AuditEvent
from app.registry.models import Project, ProjectMember
from app.vocab import AuditActionType, Classification, Priority, ProjectPhase, ProjectStatus, ProjectType, Role

PROJECT_PAYLOAD = {
    "name": "Health Fair Portal",
    "description": "Annual health fair registration site.",
    "project_type": ProjectType.INTERNAL_WEB_APP.value,
    "classification": Classification.REUSABLE.value,
    "phase": ProjectPhase.ONGOING_DEVELOPMENT.value,
    "status": ProjectStatus.ACTIVE.value,
    "priority": Priority.HIGH.value,
}


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def test_admin_can_create_project_and_audit_is_recorded(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()

    resp = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email))
    assert resp.status_code == 201
    body = resp.json()
    assert body["slug"] == "health-fair-portal"
    assert body["is_stale"] is True  # no status event yet -> no evidence

    audit = db.query(AuditEvent).filter(AuditEvent.object_id == body["id"]).one()
    assert audit.action_type == AuditActionType.PROJECT_CREATED


def test_duplicate_name_gets_suffixed_slug(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()

    first = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email))
    second = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email))
    assert first.json()["slug"] == "health-fair-portal"
    assert second.json()["slug"] == "health-fair-portal-2"


def test_manager_cannot_create_project(client: TestClient, db: Session, make_person) -> None:
    manager = make_person(Role.MANAGER)
    db.commit()

    resp = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(manager.email))
    assert resp.status_code == 403


def test_manager_sees_all_projects_developer_sees_only_membership(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    manager = make_person(Role.MANAGER)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()

    created = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email)).json()
    db.add(ProjectMember(project_id=created["id"], person_id=dev.id, role=Role.DEVELOPER_PROJECT_OWNER))
    unrelated = client.post(
        "/api/projects",
        json={**PROJECT_PAYLOAD, "name": "Unrelated Project"},
        headers=_headers(admin.email),
    ).json()
    db.commit()

    manager_list = client.get("/api/projects", headers=_headers(manager.email)).json()
    dev_list = client.get("/api/projects", headers=_headers(dev.email)).json()

    # Manager is portfolio-wide read - assert both new projects are visible rather than an
    # exact count, since the dev DB may already hold other projects (e.g. seed-imported ones).
    manager_ids = {p["id"] for p in manager_list}
    assert {created["id"], unrelated["id"]} <= manager_ids
    assert len(dev_list) == 1
    assert dev_list[0]["id"] == created["id"]


def test_developer_forbidden_from_reading_non_member_project(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()

    created = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email)).json()
    resp = client.get(f"/api/projects/{created['id']}", headers=_headers(dev.email))
    assert resp.status_code == 403


def test_get_missing_project_is_404(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()

    resp = client.get("/api/projects/999999", headers=_headers(admin.email))
    assert resp.status_code == 404


def test_update_project_records_audit_with_changed_fields(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()

    created = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email)).json()
    resp = client.patch(
        f"/api/projects/{created['id']}",
        json={"current_next_action": "Ship v1.1", "status": ProjectStatus.BLOCKED.value},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["current_next_action"] == "Ship v1.1"
    assert body["status"] == ProjectStatus.BLOCKED.value

    audit = (
        db.query(AuditEvent)
        .filter(AuditEvent.object_id == created["id"], AuditEvent.action_type == AuditActionType.PROJECT_UPDATED)
        .one()
    )
    assert set(audit.metadata_json["fields"]) == {"current_next_action", "status"}


def test_slug_is_immutable_via_update(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()

    created = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email)).json()
    resp = client.patch(
        f"/api/projects/{created['id']}",
        json={"name": "Renamed Project"},
        headers=_headers(admin.email),
    )
    assert resp.json()["slug"] == created["slug"]
