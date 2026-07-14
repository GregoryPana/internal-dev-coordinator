"""Integration settings service: DB-first config resolution with env
fallback, encrypted credential storage, connection testing."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.integrations import crypto
from app.integrations.models import IntegrationSetting

GITHUB = "github"


@dataclass
class GitHubConfig:
    enabled: bool
    token: str  # plaintext, resolved just-in-time; never persisted or logged
    api_base: str
    source: str  # "app" (DB row) | "env"


def _get_row(db: Session, provider: str) -> IntegrationSetting | None:
    return db.scalar(select(IntegrationSetting).where(IntegrationSetting.provider == provider))


def resolve_github(db: Session) -> GitHubConfig:
    """In-app settings win when a row exists; env vars remain the fallback
    so env-configured deployments keep working unchanged."""
    row = _get_row(db, GITHUB)
    if row is not None:
        token = crypto.decrypt(row.encrypted_credential) if row.encrypted_credential else ""
        api_base = (row.config_json or {}).get("api_base") or settings.github_api_base
        return GitHubConfig(enabled=row.enabled, token=token, api_base=api_base, source="app")
    return GitHubConfig(
        enabled=settings.github_provider == "github",
        token=settings.github_token,
        api_base=settings.github_api_base,
        source="env",
    )


def github_status(db: Session) -> dict:
    """Safe-to-serialize status: reports whether a credential is stored,
    never any part of the credential itself."""
    row = _get_row(db, GITHUB)
    config = resolve_github(db)
    return {
        "provider": GITHUB,
        "enabled": config.enabled,
        "source": config.source,
        "credential_set": bool(config.token),
        "api_base": config.api_base,
        "updated_at": row.updated_at.isoformat() if row is not None else None,
        "secret_key_configured": bool(settings.secret_key),
    }


def save_github(
    db: Session,
    *,
    enabled: bool,
    token: str | None,
    updated_by: int,
) -> IntegrationSetting:
    """Create/update the GitHub integration row. token=None keeps the
    existing stored credential; token="" clears it; any other value is
    encrypted and stored. Raises SecretKeyMissingError when a token is
    provided but IDC_SECRET_KEY is absent."""
    row = _get_row(db, GITHUB)
    if row is None:
        row = IntegrationSetting(provider=GITHUB, enabled=False)
        db.add(row)

    if token is not None:
        row.encrypted_credential = crypto.encrypt(token) if token else None
    row.enabled = enabled
    row.updated_by = updated_by
    db.flush()
    return row


def test_github(db: Session) -> dict:
    """Live connectivity check with the currently-resolved config: hits the
    cheapest authenticated endpoint and reports rate-limit headroom."""
    import httpx

    config = resolve_github(db)
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if config.token:
        headers["Authorization"] = f"Bearer {config.token}"
    try:
        resp = httpx.get(f"{config.api_base}/rate_limit", headers=headers, timeout=10.0)
    except httpx.HTTPError as e:
        return {"ok": False, "detail": f"Could not reach GitHub: {e}"}
    if resp.status_code == 401:
        return {"ok": False, "detail": "GitHub rejected the token (401). Check the PAT value and expiry."}
    if resp.status_code != 200:
        return {"ok": False, "detail": f"GitHub answered {resp.status_code}."}
    core = (resp.json().get("resources") or {}).get("core") or {}
    return {
        "ok": True,
        "detail": (
            f"Connected{' with token' if config.token else ' (unauthenticated - public repos only)'}. "
            f"Rate limit {core.get('remaining', '?')}/{core.get('limit', '?')} remaining."
        ),
        "authenticated": bool(config.token),
        "rate_limit_remaining": core.get("remaining"),
    }
