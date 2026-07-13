"""Microsoft Entra ID (Azure AD) token validation for auth_mode=entra.

Validates Bearer JWTs issued by the CWS tenant: signature against the
tenant's published JWKS, issuer, audience (the app registration's client
ID) and expiry. The token only establishes *identity* (email); every
permission decision still goes through the role model in
app.authz.service, and the email must match an active Person row -
a valid corporate token for someone not provisioned here is still a 401.

Requires IDC_ENTRA_TENANT_ID and IDC_ENTRA_CLIENT_ID.
"""

from functools import lru_cache

import jwt
from fastapi import HTTPException, status

from app.config import settings


class EntraConfigError(Exception):
    """auth_mode=entra without tenant/client configuration."""


def _issuer(tenant_id: str) -> str:
    return f"https://login.microsoftonline.com/{tenant_id}/v2.0"


def _jwks_url(tenant_id: str) -> str:
    return f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"


@lru_cache(maxsize=1)
def _jwks_client(tenant_id: str) -> jwt.PyJWKClient:
    # PyJWKClient caches fetched signing keys internally; lru_cache keeps one
    # client (and therefore one key cache) per process.
    return jwt.PyJWKClient(_jwks_url(tenant_id), cache_keys=True)


def validate_token(token: str) -> str:
    """Validate an Entra access token and return the user's email (lowercase).

    Raises HTTPException(401) for anything invalid - callers never see the
    reason split between signature/expiry/audience beyond the detail text.
    """
    tenant_id = settings.entra_tenant_id
    client_id = settings.entra_client_id
    if not tenant_id or not client_id:
        raise EntraConfigError(
            "auth_mode=entra requires IDC_ENTRA_TENANT_ID and IDC_ENTRA_CLIENT_ID."
        )

    try:
        signing_key = _jwks_client(tenant_id).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=_issuer(tenant_id),
            options={"require": ["exp", "iss", "aud"]},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Entra token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    email = (claims.get("preferred_username") or claims.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Entra token carries no email/preferred_username claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email
