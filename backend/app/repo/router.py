"""Repo-signals API (Phase 4 + active tracking). Read-only; authz-gated
like every other project read. Serving order:

1. fresh persisted snapshot (written by the background poller or a prior
   view within the poll interval) - no GitHub call
2. otherwise a live fetch, persisted as a new snapshot

Distinct failure modes so the frontend can hide vs. warn:
- 501: integration not enabled (in-app setting or IDC_GITHUB_PROVIDER)
- 204: project has no parseable github.com repo_url - nothing to show
- 502: enabled and repo known, but GitHub could not be queried
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.authz import service as authz
from app.db import get_db
from app.integrations import service as integrations_service
from app.registry import service as registry_service
from app.registry.models import Person
from app.repo import service as repo_service
from app.repo.provider import parse_github_repo
from app.repo.schemas import RepoSignals

router = APIRouter(prefix="/api/projects/{project_id}/repo-signals", tags=["repo-signals"])


@router.get("", response_model=RepoSignals)
def get_repo_signals(
    project_id: int,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> RepoSignals | Response:
    project = registry_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    authz.require_read(db, user, project)

    if parse_github_repo(project.repo_url) is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if not integrations_service.resolve_github(db).enabled:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub integration is disabled. An admin can enable it under Settings.",
        )

    cached = repo_service.latest_snapshot(db, project.id)
    if repo_service.snapshot_is_fresh(cached):
        signals = repo_service.signals_from_snapshot(cached)
        if signals is not None:
            return signals

    snapshot = repo_service.fetch_and_snapshot(db, project)
    db.commit()
    if snapshot is None:  # repo URL disappeared between checks
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    if not snapshot.success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=snapshot.error or "GitHub could not be queried.",
        )
    return repo_service.signals_from_snapshot(snapshot)
