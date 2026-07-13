"""Schemas for read-only repository signals (Phase 4)."""

from datetime import datetime

from pydantic import BaseModel


class LastCommit(BaseModel):
    sha: str
    message: str
    author: str | None
    committed_at: datetime | None


class RepoSignals(BaseModel):
    repo_full_name: str  # "owner/repo" parsed from the project's repo_url
    default_branch: str
    pushed_at: datetime | None
    last_commit: LastCommit | None
    open_pr_count: int
    open_issue_count: int  # excludes PRs
    fetched_at: datetime
