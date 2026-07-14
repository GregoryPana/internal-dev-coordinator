"""Active repo tracking (2026-07-14 direction): fetch results are persisted
as RepoSnapshot rows so the platform tracks repos continuously instead of
only when someone opens a profile.

Deliberate boundary: snapshots never touch Project.data_as_of - freshness
remains driven by human status evidence until that semantic change is
explicitly decided (see docs/HERMES_UPDATE_PACK.md).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.integrations.models import RepoSnapshot
from app.registry.models import Project
from app.repo.provider import (
    RepoProviderUnavailableError,
    get_repo_provider,
    parse_github_repo,
)
from app.repo.schemas import RepoSignals


def latest_snapshot(db: Session, project_id: int) -> RepoSnapshot | None:
    return db.scalar(
        select(RepoSnapshot)
        .where(RepoSnapshot.project_id == project_id)
        .order_by(RepoSnapshot.id.desc())
        .limit(1)
    )


def snapshot_is_fresh(snapshot: RepoSnapshot | None) -> bool:
    if snapshot is None or not snapshot.success:
        return False
    age = datetime.now(timezone.utc) - snapshot.fetched_at
    return age < timedelta(minutes=settings.repo_poll_interval_minutes)


def fetch_and_snapshot(db: Session, project: Project) -> RepoSnapshot | None:
    """Fetch live signals for one project and persist the outcome (success
    or failure) as a snapshot. Returns None when the project has no
    parseable github.com URL. Raises nothing - failures become failed
    snapshots so the poller and UI can see them."""
    parsed = parse_github_repo(project.repo_url)
    if parsed is None:
        return None
    owner, repo = parsed
    try:
        signals = get_repo_provider(db).fetch_signals(owner, repo)
        snapshot = RepoSnapshot(
            project_id=project.id,
            success=True,
            data_json=signals.model_dump(mode="json"),
        )
    except RepoProviderUnavailableError as e:
        snapshot = RepoSnapshot(project_id=project.id, success=False, error=str(e))
    db.add(snapshot)
    db.flush()
    return snapshot


def signals_from_snapshot(snapshot: RepoSnapshot) -> RepoSignals | None:
    if not snapshot.success or not snapshot.data_json:
        return None
    return RepoSignals.model_validate(snapshot.data_json)


@dataclass
class PollSummary:
    polled: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped_no_repo: int = 0
    errors: list[str] = field(default_factory=list)


def poll_all_projects(db: Session) -> PollSummary:
    """One tracking pass over every project with a GitHub repo URL. Commits
    per project so one bad repo can't roll back the rest."""
    summary = PollSummary()
    project_ids = list(db.scalars(select(Project.id).order_by(Project.id)))
    for project_id in project_ids:
        project = db.get(Project, project_id)
        if project is None or parse_github_repo(project.repo_url) is None:
            summary.skipped_no_repo += 1
            continue
        snapshot = fetch_and_snapshot(db, project)
        summary.polled += 1
        if snapshot is not None and snapshot.success:
            summary.succeeded += 1
        else:
            summary.failed += 1
            if snapshot is not None and snapshot.error:
                summary.errors.append(f"{project.slug}: {snapshot.error}")
        db.commit()
    return summary
