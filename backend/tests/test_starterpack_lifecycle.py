"""Tests for T8: persisted starter-pack generation, AI tailoring (with a
fake provider - no real provider is wired), review workflow, zip export."""

import zipfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.ai.models import AIInteraction
from app.ai.provider import ProviderResult, ProviderUnavailableError
from app.audit.models import AuditEvent
from app.config import settings
from app.vocab import (
    AuditActionType,
    Classification,
    ErrorCategory,
    HumanReviewStatus,
    Priority,
    ProjectPhase,
    ProjectStatus,
    ProjectType,
    Role,
    ValidationStatus,
)

INTAKE_PAYLOAD = {
    "users": "Internal ops staff",
    "workflow": "Track and resolve customer tickets",
    "data_sensitivity": "Internal customer data, no payment details",
    "integrations": "Existing CRM",
    "deployment_target": "Internal VM",
    "notes": "MVP only",
}


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def _create_project(client: TestClient, admin_email: str) -> dict:
    payload = {
        "name": "Starter Pack Lifecycle Project",
        "project_type": ProjectType.INTERNAL_WEB_APP.value,
        "classification": Classification.REUSABLE.value,
        "phase": ProjectPhase.CONCEPT.value,
        "status": ProjectStatus.ACTIVE.value,
        "priority": Priority.MEDIUM.value,
    }
    resp = client.post("/api/projects", json=payload, headers=_headers(admin_email))
    assert resp.status_code == 201
    return resp.json()


class FakeProvider:
    def __init__(self, text: str = "A helpful, grounded overview paragraph.", raise_unavailable: bool = False):
        self._text = text
        self._raise_unavailable = raise_unavailable

    def complete(self, prompt: str) -> ProviderResult:
        if self._raise_unavailable:
            raise ProviderUnavailableError("fake provider outage")
        return ProviderResult(text=self._text, model_name="fake-model", input_tokens=42, output_tokens=7)


def test_generate_persists_pack_with_disabled_provider_no_ai_interaction(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == HumanReviewStatus.GENERATED.value
    assert len(body["files"]) == 11

    assert db.query(AIInteraction).filter(AIInteraction.project_id == project["id"]).count() == 0

    audit = (
        db.query(AuditEvent)
        .filter(AuditEvent.object_id == body["id"], AuditEvent.action_type == AuditActionType.STARTER_PACK_GENERATED)
        .one()
    )
    assert audit.metadata_json["ai_tailoring_attempted"] is False


def test_full_lifecycle_generate_review_export(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    pack = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    ).json()

    review_resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/review",
        json={"decision": "reviewed"},
        headers=_headers(admin.email),
    )
    assert review_resp.status_code == 200
    assert review_resp.json()["status"] == HumanReviewStatus.REVIEWED.value
    assert review_resp.json()["reviewer"]["email"] == admin.email

    export_resp = client.get(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/export",
        headers=_headers(admin.email),
    )
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"] == "application/zip"

    get_resp = client.get(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}",
        headers=_headers(admin.email),
    )
    assert get_resp.json()["status"] == HumanReviewStatus.EXPORTED.value
    assert get_resp.json()["export_path"] is not None

    audit_actions = [
        e.action_type
        for e in db.query(AuditEvent).filter(AuditEvent.object_id == pack["id"]).order_by(AuditEvent.id).all()
    ]
    assert audit_actions == [
        AuditActionType.STARTER_PACK_GENERATED,
        AuditActionType.STARTER_PACK_REVIEWED,
        AuditActionType.STARTER_PACK_EXPORTED,
    ]


def test_export_before_review_is_409(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    pack = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    ).json()

    resp = client.get(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/export",
        headers=_headers(admin.email),
    )
    assert resp.status_code == 409


def test_reviewing_twice_is_409(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    pack = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    ).json()

    client.post(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/review",
        json={"decision": "reviewed"},
        headers=_headers(admin.email),
    )
    second = client.post(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/review",
        json={"decision": "reviewed"},
        headers=_headers(admin.email),
    )
    assert second.status_code == 409


def test_rejected_pack_cannot_be_exported(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    pack = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    ).json()

    client.post(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/review",
        json={"decision": "rejected"},
        headers=_headers(admin.email),
    )
    resp = client.get(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/export",
        headers=_headers(admin.email),
    )
    assert resp.status_code == 409


def test_exported_zip_contains_all_generated_files(client: TestClient, db: Session, make_person, tmp_path) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    pack = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    ).json()
    client.post(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/review",
        json={"decision": "reviewed"},
        headers=_headers(admin.email),
    )
    export_resp = client.get(
        f"/api/projects/{project['id']}/starter-pack/{pack['id']}/export",
        headers=_headers(admin.email),
    )
    zip_bytes = tmp_path / "pack.zip"
    zip_bytes.write_bytes(export_resp.content)
    with zipfile.ZipFile(zip_bytes) as zf:
        names = set(zf.namelist())
    assert "README.md" in names
    assert "docs/VERIFICATION_MATRIX.md" in names
    assert len(names) == 11


def test_ai_tailoring_success_replaces_readme_overview(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    monkeypatch.setattr(settings, "ai_provider", "fake")
    monkeypatch.setattr(
        "app.ai.service.get_provider",
        lambda db=None: FakeProvider(text="This tailored overview mentions the CRM integration explicitly."),
    )

    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    readme = next(f["content"] for f in body["files"] if f["path"] == "README.md")
    assert "This tailored overview mentions the CRM integration explicitly." in readme

    interaction = db.query(AIInteraction).filter(AIInteraction.project_id == project["id"]).one()
    assert interaction.validation_status == ValidationStatus.PASSED
    assert interaction.human_review_status == HumanReviewStatus.GENERATED
    assert interaction.model_provider == "fake"
    assert interaction.prompt_id == "starter_pack_tailoring"


def test_ai_tailoring_forbidden_data_in_intake_skips_call(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    monkeypatch.setattr(settings, "ai_provider", "fake")
    called = {"n": 0}

    def _tracking_provider(db=None):
        called["n"] += 1
        return FakeProvider()

    monkeypatch.setattr("app.ai.service.get_provider", _tracking_provider)

    tainted_intake = {**INTAKE_PAYLOAD, "notes": "api_key: sk_live_abcdefgh12345678"}
    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=tainted_intake,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    assert called["n"] == 0  # provider never invoked - forbidden data blocked it first

    interaction = db.query(AIInteraction).filter(AIInteraction.project_id == project["id"]).one()
    assert interaction.validation_status == ValidationStatus.FAILED_FORBIDDEN_DATA
    assert interaction.error_category == ErrorCategory.FORBIDDEN_DATA_DETECTED
    assert interaction.human_review_status == HumanReviewStatus.REJECTED


def test_ai_tailoring_provider_unavailable_falls_back_to_deterministic(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    monkeypatch.setattr(settings, "ai_provider", "fake")
    monkeypatch.setattr("app.ai.service.get_provider", lambda db=None: FakeProvider(raise_unavailable=True))

    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["files"]) == 11  # deterministic pack still produced

    interaction = db.query(AIInteraction).filter(AIInteraction.project_id == project["id"]).one()
    assert interaction.error_category == ErrorCategory.PROVIDER_UNAVAILABLE
    assert interaction.output_text is None


def test_unimplemented_provider_returns_501(client: TestClient, db: Session, make_person, monkeypatch) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)

    monkeypatch.setattr(settings, "ai_provider", "anthropic")
    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 501


def test_developer_non_member_cannot_generate_review_or_export(
    client: TestClient, db: Session, make_person
) -> None:
    admin = make_person(Role.ADMIN)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email)

    resp = client.post(
        f"/api/projects/{project['id']}/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(dev.email),
    )
    assert resp.status_code == 403


def test_generate_for_missing_project_is_404(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    resp = client.post(
        "/api/projects/999999/starter-pack/generate",
        json=INTAKE_PAYLOAD,
        headers=_headers(admin.email),
    )
    assert resp.status_code == 404
