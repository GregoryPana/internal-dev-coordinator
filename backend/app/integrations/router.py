"""Admin-only integration settings API. Credentials go IN and are never
echoed back out in any form - responses only ever say whether one is set."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.audit import service as audit_service
from app.authz import service as authz
from app.db import get_db
from app.integrations import service as integrations_service
from app.integrations.crypto import SecretKeyMissingError
from app.registry.models import Person
from app.vocab import AuditActionType, AuditObjectType

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


class GitHubSettingsUpdate(BaseModel):
    enabled: bool
    # None = keep existing stored credential; "" = clear it; other = replace.
    token: str | None = None


class AISettingsUpdate(BaseModel):
    enabled: bool
    model: str | None = None  # None = keep existing model
    # None = keep existing stored key; "" = clear it; other = replace.
    api_key: str | None = None


def _require_admin(user: Person) -> None:
    if not authz.is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Integration settings require the admin role.",
        )


@router.get("")
def list_integrations(
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> dict:
    _require_admin(user)
    return {
        "github": integrations_service.github_status(db),
        "ai": integrations_service.ai_status(db),
    }


@router.put("/github")
def update_github(
    data: GitHubSettingsUpdate,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> dict:
    _require_admin(user)
    try:
        row = integrations_service.save_github(
            db, enabled=data.enabled, token=data.token, updated_by=user.id
        )
    except SecretKeyMissingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.INTEGRATION_UPDATED,
        object_type=AuditObjectType.INTEGRATION,
        object_id=row.id,
        metadata={
            "provider": "github",
            "enabled": data.enabled,
            # Record THAT the credential changed, never anything about it.
            "credential_changed": data.token is not None,
        },
    )
    db.commit()
    return {"github": integrations_service.github_status(db)}


@router.put("/ai")
def update_ai(
    data: AISettingsUpdate,
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> dict:
    _require_admin(user)
    try:
        row = integrations_service.save_ai(
            db, enabled=data.enabled, model=data.model, api_key=data.api_key, updated_by=user.id
        )
    except SecretKeyMissingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    audit_service.record(
        db,
        actor_id=user.id,
        action_type=AuditActionType.INTEGRATION_UPDATED,
        object_type=AuditObjectType.INTEGRATION,
        object_id=row.id,
        metadata={
            "provider": "ai",
            "enabled": data.enabled,
            "model": data.model,
            "credential_changed": data.api_key is not None,
        },
    )
    db.commit()
    return {"ai": integrations_service.ai_status(db)}


@router.post("/ai/test")
def test_ai(
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> dict:
    _require_admin(user)
    try:
        return integrations_service.test_ai(db)
    except SecretKeyMissingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/github/test")
def test_github(
    db: Session = Depends(get_db),
    user: Person = Depends(authz.get_current_user),
) -> dict:
    _require_admin(user)
    try:
        return integrations_service.test_github(db)
    except SecretKeyMissingError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
