"""Fernet encryption for integration credentials at rest.

The key comes from IDC_SECRET_KEY. Saving a credential in-app without a
key configured is refused loudly (SecretKeyMissingError -> 400 at the
router) rather than falling back to plaintext storage.
"""

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


class SecretKeyMissingError(Exception):
    """IDC_SECRET_KEY is not configured - in-app credential storage disabled."""


def _fernet() -> Fernet:
    if not settings.secret_key:
        raise SecretKeyMissingError(
            "IDC_SECRET_KEY is not set. Generate one with "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
            "and add it to backend/.env, then retry."
        )
    return Fernet(settings.secret_key.encode("utf-8"))


def encrypt(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as e:
        raise SecretKeyMissingError(
            "Stored credential cannot be decrypted - IDC_SECRET_KEY has changed "
            "since it was saved. Re-enter the credential in Settings."
        ) from e
