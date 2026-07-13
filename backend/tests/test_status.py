"""Integration tests for status events (T4): create/list, freshness recompute."""

from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.audit.models import AuditEvent
from app.registry.models import ProjectMember
from app.vocab import (
    AuditActionType,
    Classification,
    Priority,
    ProjectPhase,
    ProjectStatus,
    ProjectType,
    Role,
)

PROJECT_PAYLOAD = {
    "name": "VAS",
    "project_type": ProjectType.OPERATIONAL_TOOL.value,
    "classification": Classification.REUSABLE.value,
    "phase": ProjectPhase.LIVE.value,
    "status": ProjectStatus.ACTIVE.value,
    "priority": Priority.MEDIUM.value,
}


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def _create_project(client: TestClient, admin_email: str) -> dict:
    resp = client.post("/api/projects", json=PROJECT_PAYLOAD, headers=_headers(admin_email))
    assert resp.status_code == 201
    return resp.json()


def test_create_status_event_updates_project_freshness(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    assert project["is_stale"] is True
    assert project["data_as_of"] is None

    event_date = date.today().isoformat()
    resp = client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": event_date, "summary": "Kickoff complete."},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["summary"] == "Kickoff complete."
    assert body["author"]["email"] == admin.email

    refreshed = client.get(f"/api/projects/{project['id']}", headers=_headers(admin.email)).json()
    assert refreshed["is_stale"] is False
    assert refreshed["data_as_of"].startswith(event_date)


def test_stale_flag_fires_past_freshness_threshold(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    old_date = (date.today() - timedelta(days=20)).isoformat()
    client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": old_date, "summary": "Old update."},
        headers=_headers(admin.email),
    )

    refreshed = client.get(f"/api/projects/{project['id']}", headers=_headers(admin.email)).json()
    assert refreshed["is_stale"] is True
    assert refreshed["data_as_of"].startswith(old_date)


def test_data_as_of_tracks_latest_event_regardless_of_insertion_order(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    recent = date.today().isoformat()
    older = (date.today() - timedelta(days=5)).isoformat()

    client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": recent, "summary": "Recent update."},
        headers=_headers(admin.email),
    )
    client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": older, "summary": "Backfilled older update."},
        headers=_headers(admin.email),
    )

    refreshed = client.get(f"/api/projects/{project['id']}", headers=_headers(admin.email)).json()
    assert refreshed["data_as_of"].startswith(recent)


def test_list_status_events_ordered_newest_first(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    for i, summary in enumerate(["First", "Second", "Third"]):
        d = (date.today() - timedelta(days=2 - i)).isoformat()
        client.post(
            f"/api/projects/{project['id']}/status-events",
            json={"event_date": d, "summary": summary},
            headers=_headers(admin.email),
        )

    resp = client.get(f"/api/projects/{project['id']}/status-events", headers=_headers(admin.email))
    assert resp.status_code == 200
    summaries = [e["summary"] for e in resp.json()]
    assert summaries == ["Third", "Second", "First"]


def test_status_event_create_is_audited(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    resp = client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": date.today().isoformat(), "summary": "Audited update."},
        headers=_headers(admin.email),
    )
    event_id = resp.json()["id"]

    audit = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.object_id == event_id,
            AuditEvent.action_type == AuditActionType.STATUS_EVENT_CREATED,
        )
        .one()
    )
    assert audit.project_id == project["id"]


def test_developer_non_member_cannot_create_status_event(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email)

    resp = client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": date.today().isoformat(), "summary": "Should be forbidden."},
        headers=_headers(dev.email),
    )
    assert resp.status_code == 403


def test_developer_member_can_create_status_event(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email)
    db.add(ProjectMember(project_id=project["id"], person_id=dev.id, role=Role.DEVELOPER_PROJECT_OWNER))
    db.commit()

    resp = client.post(
        f"/api/projects/{project['id']}/status-events",
        json={"event_date": date.today().isoformat(), "summary": "Member update."},
        headers=_headers(dev.email),
    )
    assert resp.status_code == 201


def test_status_events_for_missing_project_is_404(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    resp = client.get("/api/projects/999999/status-events", headers=_headers(admin.email))
    assert resp.status_code == 404
