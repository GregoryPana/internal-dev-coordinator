"""Tests for the T9 AI project-summary task: structured output validation,
stale caveats, forbidden-data handling, review workflow. Uses a fake
provider - no real network calls."""

import json

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

VALID_SUMMARY_JSON = json.dumps(
    {
        "summary": "The project is progressing with the core workflow scaffolded.",
        "assumptions": [],
        "gaps": [],
        "recommended_next_actions": ["Finish the pending integration."],
        "requires_human_review": True,
        "confidence": 0.7,
    }
)


class FakeProvider:
    def __init__(self, text: str = VALID_SUMMARY_JSON, raise_unavailable: bool = False):
        self._text = text
        self._raise_unavailable = raise_unavailable

    def complete(self, prompt: str) -> ProviderResult:
        if self._raise_unavailable:
            raise ProviderUnavailableError("fake outage")
        return ProviderResult(text=self._text, model_name="fake-model", input_tokens=100, output_tokens=40)


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def _create_project(client: TestClient, admin_email: str, **overrides) -> dict:
    payload = {
        "name": "AI Summary Test Project",
        "project_type": ProjectType.INTERNAL_WEB_APP.value,
        "classification": Classification.REUSABLE.value,
        "phase": ProjectPhase.ONGOING_DEVELOPMENT.value,
        "status": ProjectStatus.ACTIVE.value,
        "priority": Priority.MEDIUM.value,
        **overrides,
    }
    resp = client.post("/api/projects", json=payload, headers=_headers(admin_email))
    assert resp.status_code == 201
    return resp.json()


def _enable_fake_provider(monkeypatch, **kwargs):
    monkeypatch.setattr(settings, "ai_provider", "fake")
    monkeypatch.setattr("app.ai.summary_service.get_provider", lambda db=None: FakeProvider(**kwargs))


def test_generate_summary_success(client: TestClient, db: Session, make_person, monkeypatch) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch)

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["validation_status"] == ValidationStatus.PASSED.value
    assert body["human_review_status"] == HumanReviewStatus.GENERATED.value
    assert body["output_json"]["requires_human_review"] is True
    assert body["prompt_id"] == "project_summary__developer"
    assert body["source_ids_json"]["project_id"] == project["id"]

    audit = (
        db.query(AuditEvent)
        .filter(AuditEvent.object_id == body["id"], AuditEvent.action_type == AuditActionType.AI_RUN_CREATED)
        .one()
    )
    assert audit.metadata_json["audience"] == "developer"


def test_manager_audience_uses_manager_prompt(client: TestClient, db: Session, make_person, monkeypatch) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch)

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "manager"},
        headers=_headers(admin.email),
    )
    assert resp.json()["prompt_id"] == "project_summary__manager"


def test_stale_project_gets_deterministic_caveat(client: TestClient, db: Session, make_person, monkeypatch) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)  # no status events -> is_stale=True
    _enable_fake_provider(monkeypatch)  # model's own gaps list is empty

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    )
    gaps = resp.json()["output_json"]["gaps"]
    assert any("stale" in g.lower() for g in gaps)


def test_malformed_output_fails_schema_validation(client: TestClient, db: Session, make_person, monkeypatch) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch, text="not valid json at all")

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["validation_status"] == ValidationStatus.FAILED_SCHEMA.value
    assert body["human_review_status"] == HumanReviewStatus.REJECTED.value
    assert body["output_json"] is None


def test_forbidden_data_in_source_bundle_blocks_call(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    client.patch(
        f"/api/projects/{project['id']}",
        json={"description": "api_key: sk_live_abcdefgh12345678"},
        headers=_headers(admin.email),
    )

    monkeypatch.setattr(settings, "ai_provider", "fake")
    called = {"n": 0}

    def _tracking_provider(db=None):
        called["n"] += 1
        return FakeProvider()

    monkeypatch.setattr("app.ai.summary_service.get_provider", _tracking_provider)

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert called["n"] == 0
    assert body["validation_status"] == ValidationStatus.FAILED_FORBIDDEN_DATA.value
    assert body["human_review_status"] == HumanReviewStatus.REJECTED.value
    assert body["error_category"] == ErrorCategory.FORBIDDEN_DATA_DETECTED.value


def test_forbidden_data_in_model_output_is_rejected(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch, text="password: hunter2hunter2hunter2 " + VALID_SUMMARY_JSON)

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    )
    body = resp.json()
    assert body["validation_status"] == ValidationStatus.FAILED_FORBIDDEN_DATA.value
    assert body["output_json"] is None


def test_provider_unavailable_records_failed_run(client: TestClient, db: Session, make_person, monkeypatch) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch, raise_unavailable=True)

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["error_category"] == ErrorCategory.PROVIDER_UNAVAILABLE.value
    assert body["output_json"] is None


def test_list_and_review_lifecycle(client: TestClient, db: Session, make_person, monkeypatch) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch)

    created = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    ).json()

    listed = client.get(f"/api/projects/{project['id']}/ai/summaries", headers=_headers(admin.email)).json()
    assert any(i["id"] == created["id"] for i in listed)

    reviewed = client.post(
        f"/api/projects/{project['id']}/ai/summaries/{created['id']}/review",
        json={"decision": "reviewed"},
        headers=_headers(admin.email),
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["human_review_status"] == HumanReviewStatus.REVIEWED.value

    second_review = client.post(
        f"/api/projects/{project['id']}/ai/summaries/{created['id']}/review",
        json={"decision": "reviewed"},
        headers=_headers(admin.email),
    )
    assert second_review.status_code == 409


def test_developer_non_member_cannot_generate_summary(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    dev = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch)

    resp = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(dev.email),
    )
    assert resp.status_code == 403


def test_generate_summary_for_missing_project_is_404(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    resp = client.post(
        "/api/projects/999999/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 404


def test_list_all_ai_interactions_for_project(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    outsider = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email)
    _enable_fake_provider(monkeypatch)

    created = client.post(
        f"/api/projects/{project['id']}/ai/summary",
        json={"audience": "developer"},
        headers=_headers(admin.email),
    ).json()

    resp = client.get(f"/api/projects/{project['id']}/ai/interactions", headers=_headers(admin.email))
    assert resp.status_code == 200
    interactions = resp.json()
    assert [i["id"] for i in interactions] == [created["id"]]
    assert interactions[0]["task_type"] == "project_summary"

    denied = client.get(
        f"/api/projects/{project['id']}/ai/interactions", headers=_headers(outsider.email)
    )
    assert denied.status_code == 403
