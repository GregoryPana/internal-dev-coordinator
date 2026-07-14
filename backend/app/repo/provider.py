"""Read-only GitHub API client (Phase 4).

Same adapter pattern as app.ai.provider: disabled by default, selected via
IDC_GITHUB_PROVIDER, unknown names raise NotImplementedError (router turns
that into a 501). Only GET requests exist in this module - the scope doc
forbids any write action to external systems.
"""

import re
from datetime import datetime, timezone
from typing import Protocol

import httpx

from app.config import settings
from app.repo.schemas import LastCommit, RepoSignals

# https://github.com/owner/repo, optional .git suffix or trailing slash.
_GITHUB_URL_RE = re.compile(
    r"^https?://(?:www\.)?github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+?)(?:\.git)?/?$"
)


class RepoProviderUnavailableError(Exception):
    """Raised when repo signals cannot be fetched (disabled, bad URL,
    rate limit, network failure)."""


def parse_github_repo(repo_url: str | None) -> tuple[str, str] | None:
    """Return (owner, repo) for a github.com URL, None for anything else
    (GitLab, internal servers, blank) - those simply have no signals."""
    if not repo_url:
        return None
    match = _GITHUB_URL_RE.match(repo_url.strip())
    if match is None:
        return None
    return match.group("owner"), match.group("repo")


class RepoSignalsProvider(Protocol):
    def fetch_signals(self, owner: str, repo: str) -> RepoSignals: ...


class DisabledRepoProvider:
    def fetch_signals(self, owner: str, repo: str) -> RepoSignals:
        raise RepoProviderUnavailableError(
            "GitHub integration is disabled (IDC_GITHUB_PROVIDER=disabled)."
        )


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class GitHubRepoProvider:
    """Plain httpx against the GitHub REST API. A token is optional (public
    repos work unauthenticated at a much lower rate limit) but expected for
    CWS private repos: a fine-grained PAT with read-only scopes."""

    def __init__(self, api_base: str, token: str):
        self._api_base = api_base.rstrip("/")
        self._token = token

    def _get(self, client: httpx.Client, path: str, **params) -> httpx.Response:
        resp = client.get(f"{self._api_base}{path}", params=params or None)
        if resp.status_code == 404:
            raise RepoProviderUnavailableError(
                "Repository not found on GitHub (or the token cannot see it)."
            )
        if resp.status_code in (401, 403):
            raise RepoProviderUnavailableError(
                f"GitHub rejected the request ({resp.status_code}) - check IDC_GITHUB_TOKEN "
                "scope or rate limits."
            )
        resp.raise_for_status()
        return resp

    def fetch_signals(self, owner: str, repo: str) -> RepoSignals:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            with httpx.Client(headers=headers, timeout=15.0) as client:
                repo_data = self._get(client, f"/repos/{owner}/{repo}").json()

                commits = self._get(
                    client, f"/repos/{owner}/{repo}/commits", per_page=1
                ).json()
                last_commit = None
                if commits:
                    c = commits[0]
                    commit_info = c.get("commit", {})
                    author_info = commit_info.get("author") or {}
                    last_commit = LastCommit(
                        sha=c.get("sha", "")[:12],
                        message=(commit_info.get("message") or "").splitlines()[0][:200],
                        author=author_info.get("name"),
                        committed_at=_parse_dt(author_info.get("date")),
                    )

                pulls = self._get(
                    client, f"/repos/{owner}/{repo}/pulls", state="open", per_page=100
                ).json()
        except httpx.HTTPError as e:
            raise RepoProviderUnavailableError(f"GitHub request failed: {e}") from e

        open_prs = len(pulls)
        # GitHub's open_issues_count includes PRs; report issues without them.
        open_issues = max(0, (repo_data.get("open_issues_count") or 0) - open_prs)
        return RepoSignals(
            repo_full_name=repo_data.get("full_name") or f"{owner}/{repo}",
            default_branch=repo_data.get("default_branch") or "main",
            pushed_at=_parse_dt(repo_data.get("pushed_at")),
            last_commit=last_commit,
            open_pr_count=open_prs,
            open_issue_count=open_issues,
            fetched_at=datetime.now(timezone.utc),
        )


def get_repo_provider(db=None) -> RepoSignalsProvider:
    """Resolve the provider from in-app integration settings (DB row wins)
    with env-var fallback. Pass a Session to honor in-app settings; without
    one, only env config is consulted (kept for compatibility)."""
    if db is not None:
        from app.integrations import service as integrations_service

        config = integrations_service.resolve_github(db)
        if config.enabled:
            return GitHubRepoProvider(api_base=config.api_base, token=config.token)
        # An explicit in-app row overrides env entirely; env only applies
        # when no row exists (resolve_github already encodes that).
        if config.source == "app":
            return DisabledRepoProvider()

    if settings.github_provider == "disabled":
        return DisabledRepoProvider()
    if settings.github_provider == "github":
        return GitHubRepoProvider(api_base=settings.github_api_base, token=settings.github_token)
    raise NotImplementedError(
        f"Repo provider '{settings.github_provider}' is not implemented. Only 'disabled' "
        "and 'github' are wired."
    )
