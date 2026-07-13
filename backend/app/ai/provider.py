"""AI provider adapter (FR-015, architecture spec section 11.6).

Only 'disabled' is implemented. No API key/budget/data-handling route has
been approved yet (see the MVP Implementation Plan's open items and
docs/HERMES_UPDATE_PACK.md's T8 entry) - wiring a real provider means
picking one, adding its SDK to requirements.txt, and getting a key, none
of which this task does. The adapter shape exists so that work is a
provider-file addition, not a redesign.
"""

from dataclasses import dataclass
from typing import Protocol

from app.config import settings


class ProviderUnavailableError(Exception):
    """Raised when the configured provider cannot fulfil a request."""


@dataclass
class ProviderResult:
    text: str
    model_name: str
    input_tokens: int
    output_tokens: int


class AIProvider(Protocol):
    def complete(self, prompt: str) -> ProviderResult: ...


class DisabledProvider:
    """The MVP default (IDC_AI_PROVIDER=disabled). Never called in practice -
    app.ai.service short-circuits before reaching a provider when disabled -
    but kept so get_provider() always returns something Protocol-shaped."""

    def complete(self, prompt: str) -> ProviderResult:
        raise ProviderUnavailableError("AI provider is disabled (IDC_AI_PROVIDER=disabled).")


def get_provider() -> AIProvider:
    if settings.ai_provider == "disabled":
        return DisabledProvider()
    raise NotImplementedError(
        f"AI provider '{settings.ai_provider}' is not implemented. Only 'disabled' is wired "
        "until a production provider route is approved (add its SDK + client here when it is)."
    )
