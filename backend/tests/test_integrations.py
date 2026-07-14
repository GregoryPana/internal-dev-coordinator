"""In-app integration settings: encrypted storage, admin-only API,
credential never echoed, DB-over-env resolution, snapshot persistence."""

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import pytest

from app.config import settings
from app.integrations import crypto
from app.integrations import service as integrations_service
from app.integrations.crypto import SecretKeyMissingError
from app.integrations.models import RepoSnapshot
from app.repo import service as repo_service
from app.repo.provider import get_repo_provider
from app.vocab import Classification, Priority, ProjectPhase, ProjectStatus, ProjectType, Role

TEST_KEY = Fernet.generate_key().decode()


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


@pytest.fixture()
def secret_key(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", TEST_KEY)


@pytest.fixture()
def no_integration_rows(db: Session):
    """The shared dev DB may hold a real committed integration row (the
    SAVEPOINT fixture sees committed data - same lesson as T6). Delete it
    inside the test transaction; the rollback restores it afterwards."""
    from app.integrations.models import IntegrationSetting

    db.query(IntegrationSetting).delete()
    db.flush()


def test_crypto_roundtrip(secret_key) -> None:
    assert crypto.decrypt(crypto.encrypt("github_pat_abc123")) == "github_pat_abc123"


def test_crypto_requires_key() -> None:
    with pytest.raises(SecretKeyMissingError):
        crypto.encrypt("anything")


def test_settings_api_admin_only_and_never_echoes_token(
    client: TestClient, db: Session, make_person, secret_key
) -> None:
    admin = make_person(Role.ADMIN)
    developer = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()

    assert client.get("/api/integrations", headers=_headers(developer.email)).status_code == 403

    resp = client.put(
        "/api/integrations/github",
        json={"enabled": True, "token": "github_pat_supersecret"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 200
    body = resp.json()["github"]
    assert body["enabled"] is True
    assert body["credential_set"] is True
    assert body["source"] == "app"
    # The token must not appear anywhere in the response.
    assert "supersecret" not in resp.text

    status = client.get("/api/integrations", headers=_headers(admin.email)).json()["github"]
    assert status["credential_set"] is True
    assert "supersecret" not in str(status)

    # Audit records the change but nothing about the credential value.
    from app.audit.models import AuditEvent

    event = (
        db.query(AuditEvent)
        .filter(AuditEvent.action_type == "integration_updated")
        .order_by(AuditEvent.id.desc())
        .first()
    )
    assert event is not None
    assert event.metadata_json["credential_changed"] is True
    assert "supersecret" not in str(event.metadata_json)


def test_save_requires_secret_key(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    resp = client.put(
        "/api/integrations/github",
        json={"enabled": True, "token": "github_pat_x"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 400
    assert "IDC_SECRET_KEY" in resp.json()["detail"]


def test_resolution_db_overrides_env(
    db: Session, make_person, monkeypatch, secret_key, no_integration_rows
) -> None:
    admin = make_person(Role.ADMIN)
    # Env says enabled with token A...
    monkeypatch.setattr(settings, "github_provider", "github")
    monkeypatch.setattr(settings, "github_token", "env-token")
    config = integrations_service.resolve_github(db)
    assert (config.source, config.enabled, config.token) == ("env", True, "env-token")

    # ...but once an in-app row exists, it wins - even to disable.
    integrations_service.save_github(db, enabled=False, token="app-token", updated_by=admin.id)
    config = integrations_service.resolve_github(db)
    assert (config.source, config.enabled, config.token) == ("app", False, "app-token")
    assert type(get_repo_provider(db)).__name__ == "DisabledRepoProvider"

    integrations_service.save_github(db, enabled=True, token=None, updated_by=admin.id)
    config = integrations_service.resolve_github(db)
    assert (config.enabled, config.token) == (True, "app-token")  # token=None kept it
    assert type(get_repo_provider(db)).__name__ == "GitHubRepoProvider"

    integrations_service.save_github(db, enabled=True, token="", updated_by=admin.id)
    assert integrations_service.resolve_github(db).token == ""  # token="" cleared it


class FakeProviderOK:
    def fetch_signals(self, owner, repo):
        from datetime import datetime, timezone

        from app.repo.schemas import RepoSignals

        return RepoSignals(
            repo_full_name=f"{owner}/{repo}",
            default_branch="main",
            pushed_at=None,
            last_commit=None,
            open_pr_count=1,
            open_issue_count=0,
            fetched_at=datetime.now(timezone.utc),
        )


def test_snapshot_persistence_and_freshness(
    client: TestClient, db: Session, make_person, monkeypatch, secret_key
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = client.post(
        "/api/projects",
        json={
            "name": "Snapshot Test Project",
            "project_type": ProjectType.OPERATIONAL_TOOL.value,
            "classification": Classification.REUSABLE.value,
            "phase": ProjectPhase.ONGOING_DEVELOPMENT.value,
            "status": ProjectStatus.ACTIVE.value,
            "priority": Priority.MEDIUM.value,
            "repo_url": "https://github.com/cws/snapshot-test",
        },
        headers=_headers(admin.email),
    ).json()

    integrations_service.save_github(db, enabled=True, token="t", updated_by=admin.id)
    db.commit()
    monkeypatch.setattr("app.repo.service.get_repo_provider", lambda db=None: FakeProviderOK())

    # First call: live fetch, persisted as a snapshot.
    resp = client.get(f"/api/projects/{project['id']}/repo-signals", headers=_headers(admin.email))
    assert resp.status_code == 200
    snapshots = db.query(RepoSnapshot).filter(RepoSnapshot.project_id == project["id"]).all()
    assert len(snapshots) == 1 and snapshots[0].success

    # Second call within the poll interval: served from cache, no new row.
    resp = client.get(f"/api/projects/{project['id']}/repo-signals", headers=_headers(admin.email))
    assert resp.status_code == 200
    assert db.query(RepoSnapshot).filter(RepoSnapshot.project_id == project["id"]).count() == 1


def test_poll_all_projects_snapshots_and_survives_failures(
    db: Session, make_person, monkeypatch, secret_key
) -> None:
    from app.registry.models import Project
    from app.repo.provider import RepoProviderUnavailableError

    admin = make_person(Role.ADMIN)
    good = Project(
        slug="poll-good", name="Poll Good",
        project_type=ProjectType.PROTOTYPE, classification=Classification.ONE_OFF,
        phase=ProjectPhase.CONCEPT, status=ProjectStatus.ACTIVE, priority=Priority.LOW,
        repo_url="https://github.com/cws/good",
    )
    bad = Project(
        slug="poll-bad", name="Poll Bad",
        project_type=ProjectType.PROTOTYPE, classification=Classification.ONE_OFF,
        phase=ProjectPhase.CONCEPT, status=ProjectStatus.ACTIVE, priority=Priority.LOW,
        repo_url="https://github.com/cws/bad",
    )
    norepo = Project(
        slug="poll-norepo", name="Poll No Repo",
        project_type=ProjectType.PROTOTYPE, classification=Classification.ONE_OFF,
        phase=ProjectPhase.CONCEPT, status=ProjectStatus.ACTIVE, priority=Priority.LOW,
    )
    db.add_all([good, bad, norepo])
    db.flush()

    class MixedProvider:
        def fetch_signals(self, owner, repo):
            if repo == "bad":
                raise RepoProviderUnavailableError("GitHub request failed: nope")
            return FakeProviderOK().fetch_signals(owner, repo)

    monkeypatch.setattr("app.repo.service.get_repo_provider", lambda db=None: MixedProvider())
    summary = repo_service.poll_all_projects(db)

    assert summary.succeeded >= 1
    assert summary.failed >= 1
    assert summary.skipped_no_repo >= 1
    good_snap = repo_service.latest_snapshot(db, good.id)
    bad_snap = repo_service.latest_snapshot(db, bad.id)
    assert good_snap.success is True
    assert bad_snap.success is False and "nope" in bad_snap.error
    assert repo_service.latest_snapshot(db, norepo.id) is None
    _ = admin  # silence unused warning


def test_ai_settings_save_resolve_and_no_key_echo(
    client: TestClient, db: Session, make_person, secret_key, no_integration_rows, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()

    # Env fallback first.
    monkeypatch.setattr(settings, "ai_provider", "openrouter")
    monkeypatch.setattr(settings, "ai_model", "env-model")
    monkeypatch.setattr(settings, "ai_api_key", "env-key")
    cfg = integrations_service.resolve_ai(db)
    assert (cfg.source, cfg.provider, cfg.model, cfg.api_key) == ("env", "openrouter", "env-model", "env-key")

    # In-app row wins.
    resp = client.put(
        "/api/integrations/ai",
        json={"enabled": True, "model": "nvidia/nemotron-nano-9b-v2:free", "api_key": "sk-or-verysecret"},
        headers=_headers(admin.email),
    )
    assert resp.status_code == 200
    assert "verysecret" not in resp.text
    body = resp.json()["ai"]
    assert body["enabled"] is True and body["source"] == "app"
    assert body["model"] == "nvidia/nemotron-nano-9b-v2:free"
    assert body["credential_set"] is True

    cfg = integrations_service.resolve_ai(db)
    assert (cfg.source, cfg.provider, cfg.api_key) == ("app", "openrouter", "sk-or-verysecret")

    # Disabling in-app beats env enablement; provider resolves to Disabled.
    client.put("/api/integrations/ai", json={"enabled": False}, headers=_headers(admin.email))
    from app.ai.provider import get_provider as ai_get_provider

    assert type(ai_get_provider(db)).__name__ == "DisabledProvider"
    # model kept, key kept (api_key omitted = None)
    cfg = integrations_service.resolve_ai(db)
    assert cfg.model == "nvidia/nemotron-nano-9b-v2:free"
    assert cfg.api_key == "sk-or-verysecret"

    denied = client.get("/api/integrations", headers=_headers(make_person(Role.DEVELOPER_PROJECT_OWNER).email))
    assert denied.status_code == 403
