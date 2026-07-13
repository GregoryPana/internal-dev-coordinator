"""Forbidden-data scanning (AGENTS.md: never send or store secrets, .env
content, tokens, passwords, private keys or unnecessary PII). Applied to
user-entered free text, the AI input bundle, and AI output before either
is sent, stored or trusted.
"""

import re

_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key block"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key ID"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "JWT-like token"),
    (
        re.compile(
            r"(?i)\b(api[_-]?key|secret|password|passwd|client[_-]?secret|access[_-]?token)\b\s*[:=]\s*"
            r"['\"]?[A-Za-z0-9+/=_\-]{8,}"
        ),
        "key/secret-like assignment",
    ),
]


def scan(text: str) -> list[str]:
    """Return the list of forbidden-data pattern labels found in text."""
    return [label for pattern, label in _PATTERNS if pattern.search(text)]


def scan_many(texts: dict[str, str]) -> dict[str, list[str]]:
    """Scan several named texts; return only the ones with findings."""
    results = {name: scan(text) for name, text in texts.items()}
    return {name: findings for name, findings in results.items() if findings}
