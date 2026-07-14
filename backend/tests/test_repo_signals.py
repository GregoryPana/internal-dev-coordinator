"""Phase 4 GitHub read integration: URL parsing, provider selection,
endpoint status codes. Uses a fake provider - no real network calls."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.repo.provider import (
    RepoProviderUnavailableError,
    get_repo_provider,
    parse_github_repo,
)
from app.repo.schemas import LastCommit, RepoSignals
from app.vocab import Classification, Priority, ProjectPhase, ProjectStatus, ProjectType, Role


def _headers(email: str) -> dict:
    return {"X-User-Email": email}


def _create_project(client: TestClient, admin_email: str, **overrides) -> dict:
    payload = {
        "name": "Repo Signals Test Project",
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


FAKE_SIGNALS = RepoSignals(
    repo_full_name="cws/network-check",
    default_branch="main",
    pushed_at=datetime(2026, 7, 10, tzinfo=timezone.utc),
    last_commit=LastCommit(
        sha="abc123def456",
        message="fix: SMSC auth retry",
        author="Gregory Panagary",
        committed_at=datetime(2026, 7, 10, tzinfo=timezone.utc),
    ),
    open_pr_count=2,
    open_issue_count=1,
    fetched_at=datetime(2026, 7, 13, tzinfo=timezone.utc),
)


class FakeRepoProvider:
    def __init__(self, raise_unavailable: bool = False):
        self._raise = raise_unavailable

    def fetch_signals(self, owner: str, repo: str) -> RepoSignals:
        if self._raise:
            raise RepoProviderUnavailableError("GitHub request failed: fake outage")
        return FAKE_SIGNALS


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/cws/network-check", ("cws", "network-check")),
        ("https://github.com/cws/network-check.git", ("cws", "network-check")),
        ("https://github.com/cws/network-check/", ("cws", "network-check")),
        ("http://www.github.com/CWS-Org/some.repo-name", ("CWS-Org", "some.repo-name")),
        ("https://gitlab.com/cws/network-check", None),
        ("https://github.com/cws", None),
        ("not a url", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_github_repo(url, expected) -> None:
    assert parse_github_repo(url) == expected


def test_get_repo_provider_selection(monkeypatch) -> None:
    monkeypatch.setattr(settings, "github_provider", "disabled")
    with pytest.raises(RepoProviderUnavailableError):
        get_repo_provider().fetch_signals("cws", "x")

    monkeypatch.setattr(settings, "github_provider", "github")
    provider = get_repo_provider()
    assert type(provider).__name__ == "GitHubRepoProvider"

    monkeypatch.setattr(settings, "github_provider", "bitbucket")
    with pytest.raises(NotImplementedError):
        get_repo_provider()


def test_endpoint_204_when_no_github_repo_url(client: TestClient, db: Session, make_person) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    for repo_url in (None, "https://gitlab.internal.cws/x/y"):
        project = _create_project(client, admin.email, repo_url=repo_url)
        resp = client.get(f"/api/projects/{project['id']}/repo-signals", headers=_headers(admin.email))
        assert resp.status_code == 204


def test_endpoint_501_when_disabled(client: TestClient, db: Session, make_person) -> None:
    # Clear any committed in-app integration row inside this test's
    # transaction (rolled back afterwards) so env-fallback "disabled" applies.
    from app.integrations.models import IntegrationSetting

    db.query(IntegrationSetting).delete()
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, repo_url="https://github.com/cws/network-check")
    resp = client.get(f"/api/projects/{project['id']}/repo-signals", headers=_headers(admin.email))
    assert resp.status_code == 501


def test_endpoint_returns_signals_with_provider(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    outsider = make_person(Role.DEVELOPER_PROJECT_OWNER)
    db.commit()
    project = _create_project(client, admin.email, repo_url="https://github.com/cws/network-check")

    monkeypatch.setattr(settings, "github_provider", "github")
    monkeypatch.setattr("app.repo.service.get_repo_provider", lambda db=None: FakeRepoProvider())

    resp = client.get(f"/api/projects/{project['id']}/repo-signals", headers=_headers(admin.email))
    assert resp.status_code == 200
    body = resp.json()
    assert body["repo_full_name"] == "cws/network-check"
    assert body["last_commit"]["sha"] == "abc123def456"
    assert body["open_pr_count"] == 2

    denied = client.get(
        f"/api/projects/{project['id']}/repo-signals", headers=_headers(outsider.email)
    )
    assert denied.status_code == 403


def test_endpoint_502_when_github_unreachable(
    client: TestClient, db: Session, make_person, monkeypatch
) -> None:
    admin = make_person(Role.ADMIN)
    db.commit()
    project = _create_project(client, admin.email, repo_url="https://github.com/cws/network-check")

    monkeypatch.setattr(settings, "github_provider", "github")
    monkeypatch.setattr(
        "app.repo.service.get_repo_provider", lambda db=None: FakeRepoProvider(raise_unavailable=True)
    )

    resp = client.get(f"/api/projects/{project['id']}/repo-signals", headers=_headers(admin.email))
    assert resp.status_code == 502


def test_repo_package_has_no_write_calls() -> None:
    """Scope guard: the repo package must stay read-only - no POST/PUT/PATCH/
    DELETE against GitHub, ever (docs/PROJECT_SCOPE.md)."""
    import inspect

    import app.repo.provider as provider_module

    src = inspect.getsource(provider_module)
    for forbidden in (".post(", ".put(", ".patch(", ".delete(", "requests.post"):
        assert forbidden not in src
