"""AI provider adapter (FR-015, architecture spec section 11.6).

'disabled' and 'openrouter' are implemented. OpenRouter was approved by
Gregory 2026-07-13 as the MVP provider route (see docs/HERMES_UPDATE_PACK.md)
specifically because it fronts free-tier models, avoiding a budget/vendor
decision before the golden-set evaluation (T10) has run. No SDK dependency
needed - OpenRouter's API is plain HTTP and httpx is already a dependency.
"""

import time
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.config import settings

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-nano-9b-v2:free"  # gemma-4-31b started 404ing upstream 2026-07-14
# OpenRouter's free-tier models share oversubscribed upstream capacity and
# 429 often even for a fresh, unused key - observed directly while wiring
# this up (see docs/HERMES_UPDATE_PACK.md). Retry a few times before
# falling back to the deterministic pack; a real 429 clears in seconds,
# not minutes, per the provider's own retry_after_seconds.
_MAX_RETRIES = 3
_RETRY_BACKOFF_SECONDS = 2.0


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
    """The MVP-original default (IDC_AI_PROVIDER=disabled). Never called in
    practice - app.ai.service short-circuits before reaching a provider when
    disabled - but kept so get_provider() always returns something
    Protocol-shaped."""

    def complete(self, prompt: str) -> ProviderResult:
        raise ProviderUnavailableError("AI provider is disabled (IDC_AI_PROVIDER=disabled).")


class OpenRouterProvider:
    """OpenRouter (https://openrouter.ai) - OpenAI-compatible chat completions
    API fronting many models, including a free tier. No prompt caching (per
    AGENTS.md); each call is independent."""

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ProviderUnavailableError("IDC_AI_API_KEY is not set - required for IDC_AI_PROVIDER=openrouter.")
        self._api_key = api_key
        self._model = model

    def complete(self, prompt: str) -> ProviderResult:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/GregoryPana/internal-dev-coordinator",
            "X-Title": "CWS Internal Development Coordinator",
        }
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
        }

        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = httpx.post(_OPENROUTER_URL, headers=headers, json=payload, timeout=60.0)
                if resp.status_code == 429 and attempt < _MAX_RETRIES:
                    retry_after = _RETRY_BACKOFF_SECONDS * (attempt + 1)
                    try:
                        retry_after = max(retry_after, float(resp.headers.get("Retry-After", 0)))
                    except ValueError:
                        pass
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
            except httpx.HTTPError as e:
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_BACKOFF_SECONDS * (attempt + 1))
                    continue
                raise ProviderUnavailableError(f"OpenRouter request failed after retries: {e}") from e

        choices = data.get("choices") or []
        if not choices:
            raise ProviderUnavailableError(f"OpenRouter returned no choices: {data}")

        message = choices[0].get("message", {})
        content = message.get("content") or ""
        usage = data.get("usage") or {}
        return ProviderResult(
            text=content,
            model_name=data.get("model", self._model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )


def get_provider() -> AIProvider:
    if settings.ai_provider == "disabled":
        return DisabledProvider()
    if settings.ai_provider == "openrouter":
        return OpenRouterProvider(
            api_key=settings.ai_api_key,
            model=settings.ai_model or _DEFAULT_OPENROUTER_MODEL,
        )
    raise NotImplementedError(
        f"AI provider '{settings.ai_provider}' is not implemented. Only 'disabled' and "
        "'openrouter' are wired (add a client here for anything else)."
    )
