"""Repo-signals API (Phase 4). Read-only; authz-gated like every other
project read. Distinct failure modes so the frontend can hide vs. warn:

- 501: integration not enabled (IDC_GITHUB_PROVIDER=disabled/unknown)
- 204: project has no parseable github.com repo_url - nothing to show
- 502: enabled and repo known, but GitHub could not be queried
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.authz import service as authz
from app.db import get_db
from app.registry import service as registry_service
from app.registry.models import Person
from app.repo.provider import (
    RepoProviderUnavailableError,
    get_repo_provider,
    parse_github_repo,
)
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

    parsed = parse_github_repo(project.repo_url)
    if parsed is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    try:
        provider = get_repo_provider()
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e)) from e

    owner, repo = parsed
    try:
        return provider.fetch_signals(owner, repo)
    except RepoProviderUnavailableError as e:
        detail = str(e)
        if "disabled" in detail:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=detail) from e
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail) from e
