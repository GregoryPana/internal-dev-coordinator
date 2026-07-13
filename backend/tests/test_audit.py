"""Audit layer: append-only contract at the app layer, plus the read-only
audit API (portfolio feed for admin/auditor, project-scoped trail for
project readers)."""

import inspect

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.audit.service as audit_service
from app.vocab import Classification, Priority, ProjectPhase, ProjectStatus, ProjectType, Role

PROJECT_PAYLOAD = {
    "name": "Audit Trail Project",
    "project_type": ProjectType.OPERATIONAL_TOOL.value,
    "classification": Classification.REUSABLE.value,
    "phase": ProjectPhase.ONGOING_DEVELOPMENT.value,
    "status": ProjectStatus.ACTIVE.value,
    "priority": Priority.MEDIUM.value,
}


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def test_audit_service_write_surface_is_record_only() -> None:
    """Append-only contract: record() is the sole write path. Read helpers
    are allowed but must be explicitly listed here so additions are
    deliberate."""
    public = sorted(
        name
        for name, obj in inspect.getmembers(audit_service, inspect.isfunction)
        if not name.startswith("_") and obj.__module__ == audit_service.__name__
    )
    assert public == ["list_events", "record"]


def test_no_update_or_delete_in_audit_service_source() -> None:
    src = inspect.getsource(audit_service)
    for forbidden in ("db.delete", ".update(", "synchronize_session"):
        assert forbidden not in src


def test_audit_router_has_no_write_routes() -> None:
    from app.audit.router import router

    for route in router.routes:
        assert route.methods <= {"GET", "HEAD"}, f"audit route {route.path} must be read-only"


def test_portfolio_audit_feed_requires_admin_or_auditor(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    auditor = make_person(Role.AUDITOR)
    developer = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()

    resp = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email))
    assert resp.status_code == 201
    project = resp.json()

    denied = client.get("/api/audit/events", headers=_headers(developer.email))
    assert denied.status_code == 403

    for allowed_email in (admin.email, auditor.email):
        resp = client.get("/api/audit/events", headers=_headers(allowed_email))
        assert resp.status_code == 200
        page = resp.json()
        assert page["total"] >= 1
        created = [
            e
            for e in page["items"]
            if e["action_type"] == "project_created" and e["project_id"] == project["id"]
        ]
        assert created, "project_created event should appear in the portfolio feed"
        assert created[0]["actor_email"] == admin.email


def test_project_audit_trail_visible_to_members_and_filters(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    outsider = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()

    project = client.post(
        "/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email)
    ).json()
    resp = client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": "2026-07-01", "summary": "Audit trail check."},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201

    # Non-member developer cannot read this project's audit trail.
    denied = client.get(
        f"/api/projects/{project['id']}/audit-events", headers=_headers(outsider.email)
    )
    assert denied.status_code == 403

    page = client.get(
        f"/api/projects/{project['id']}/audit-events", headers=_headers(admin.email)
    ).json()
    action_types = {e["action_type"] for e in page["items"]}
    assert {"project_created", "status_event_created"} <= action_types
    assert all(e["project_id"] == project["id"] for e in page["items"])

    filtered = client.get(
        f"/api/projects/{project['id']}/audit-events",
        params={"action_type": "status_event_created"},
        headers=_headers(admin.email),
    ).json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["action_type"] == "status_event_created"

    missing = client.get("/api/projects/999999/audit-events", headers=_headers(admin.email))
    assert missing.status_code == 404


def test_audit_feed_pagination(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = client.post(
        "/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin.email)
    ).json()
    for day in ("2026-07-01", "2026-07-02", "2026-07-03"):
        client.post(
            f"/api/projects/{project['id']}/status-events",
            json={"event_date": day, "summary": f"Update {day}."},
            headers=_headers(admin.email),
        )

    page = client.get(
        f"/api/projects/{project['id']}/audit-events",
        params={"limit": 2, "offset": 0},
        headers=_headers(admin.email),
    ).json()
    assert page["total"] == 4  # project_created + 3 status events
    assert len(page["items"]) == 2
    # Newest first.
    ids = [e["id"] for e in page["items"]]
    assert ids == sorted(ids, reverse=True)

    rest = client.get(
        f"/api/projects/{project['id']}/audit-events",
        params={"limit": 2, "offset": 2},
        headers=_headers(admin.email),
    ).json()
    assert len(rest["items"]) == 2
    assert set(ids).isdisjoint({e["id"] for e in rest["items"]})
