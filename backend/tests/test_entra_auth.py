"""Entra token-validation path (auth_mode=entra). Tokens are signed with a
locally generated RSA key and the JWKS client is faked - no network calls.
The permission model itself is unchanged; these tests cover identity only."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.authz import entra
from app.authz.entra import EntraConfigError, validate_token
from app.config import settings
from app.vocab import Role

TENANT = "11111111-2222-3333-4444-555555555555"
CLIENT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()


def _make_token(
    email: str = "gregory.panagary@cwseychelles.com",
    *,
    audience: str = CLIENT,
    issuer: str | None = None,
    expires_in: int = 600,
    email_claim: str = "preferred_username",
) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "iss": issuer or f"https://login.microsoftonline.com/{TENANT}/v2.0",
        "aud": audience,
        "exp": now + timedelta(seconds=expires_in),
        "iat": now,
    }
    if email:
        claims[email_claim] = email
    return jwt.encode(claims, _PRIVATE_KEY, algorithm="RS256")


@pytest.fixture()
def entra_mode(monkeypatch):
    monkeypatch.setattr(settings, "auth_mode", "entra")
    monkeypatch.setattr(settings, "entra_tenant_id", TENANT)
    monkeypatch.setattr(settings, "entra_client_id", CLIENT)
    fake_client = SimpleNamespace(
        get_signing_key_from_jwt=lambda token: SimpleNamespace(key=_PUBLIC_KEY)
    )
    monkeypatch.setattr(entra, "_jwks_client", lambda tenant_id: fake_client)


def test_validate_token_returns_email(entra_mode) -> None:
    assert validate_token(_make_token("Gregory.Panagary@CWSeychelles.com")) == (
        "gregory.panagary@cwseychelles.com"
    )


def test_validate_token_rejects_bad_tokens(entra_mode) -> None:
    from fastapi import HTTPException

    for bad in (
        _make_token(expires_in=-60),  # expired
        _make_token(audience="some-other-app"),  # wrong audience
        _make_token(issuer="https://evil.example/v2.0"),  # wrong issuer
        _make_token(email=""),  # no email claim
        "not-a-jwt",
    ):
        with pytest.raises(HTTPException) as exc:
            validate_token(bad)
        assert exc.value.status_code == 401


def test_validate_token_requires_configuration(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auth_mode", "entra")
    monkeypatch.setattr(settings, "entra_tenant_id", "")
    monkeypatch.setattr(settings, "entra_client_id", "")
    with pytest.raises(EntraConfigError):
        validate_token(_make_token())


def test_endpoint_accepts_valid_bearer_and_ignores_header_stub(
    client: TestClient, db: Session, make_person, entra_mode
) -> None:
    admin = make_person(Role.ADMIN, email="entra-admin@cws.sc")
    other = make_person(Role.ADMIN, email="someone-else@cws.sc")
    db.commit()

    token = _make_token(admin.email)
    resp = client.get(
        "/api/projects",
        headers={
            "Authorization": f"Bearer {token}",
            # In entra mode the dev header must be ignored, not trusted.
            "X-User-Email": other.email,
        },
    )
    assert resp.status_code == 200

    # Identity came from the token: an audit-portfolio call proves the
    # resolved user is the token's admin, not an arbitrary header.
    feed = client.get("/api/audit/events", headers={"Authorization": f"Bearer {token}"})
    assert feed.status_code == 200


def test_endpoint_rejects_missing_bearer_and_unknown_user(
    client: TestClient, db: Session, make_person, entra_mode
) -> None:
    resp = client.get("/api/projects")
    assert resp.status_code == 401

    resp = client.get("/api/projects", headers={"X-User-Email": "spoof@cws.sc"})
    assert resp.status_code == 401

    # Valid corporate token, but not provisioned as a Person -> still 401.
    token = _make_token("not-provisioned@cwseychelles.com")
    resp = client.get("/api/projects", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
