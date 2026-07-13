"""Tests for the OpenRouter provider adapter mechanics (request/response
parsing, error handling) - no real network calls; httpx.post is mocked."""

import httpx
import pytest

from app.ai import provider as provider_module
from app.ai.provider import OpenRouterProvider, ProviderUnavailableError


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch):
    """Retries use time.sleep for backoff - skip the real wait in tests."""
    monkeypatch.setattr(provider_module.time, "sleep", lambda seconds: None)


def _fake_response(json_body: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=json_body, request=httpx.Request("POST", "https://example.test"))


def test_complete_parses_content_and_usage(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        assert headers["Authorization"] == "Bearer test-key"
        assert json["model"] == "openai/gpt-oss-120b:free"
        assert json["messages"] == [{"role": "user", "content": "hello"}]
        return _fake_response(
            {
                "model": "openai/gpt-oss-120b:free",
                "choices": [{"message": {"content": "A tailored overview."}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 5},
            }
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-oss-120b:free")
    result = provider.complete("hello")

    assert result.text == "A tailored overview."
    assert result.input_tokens == 12
    assert result.output_tokens == 5
    assert result.model_name == "openai/gpt-oss-120b:free"


def test_missing_api_key_raises_immediately() -> None:
    with pytest.raises(ProviderUnavailableError):
        OpenRouterProvider(api_key="", model="openai/gpt-oss-120b:free")


def test_http_error_raises_provider_unavailable(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        raise httpx.ConnectTimeout("timed out")

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-oss-120b:free")
    with pytest.raises(ProviderUnavailableError):
        provider.complete("hello")


def test_non_2xx_status_raises_provider_unavailable(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        return _fake_response({"error": "rate limited"}, status_code=429)

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-oss-120b:free")
    with pytest.raises(ProviderUnavailableError):
        provider.complete("hello")


def test_no_choices_raises_provider_unavailable(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):
        return _fake_response({"choices": []})

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-oss-120b:free")
    with pytest.raises(ProviderUnavailableError):
        provider.complete("hello")


def test_429_is_retried_and_then_succeeds(monkeypatch) -> None:
    """OpenRouter free-tier models 429 intermittently even for a fresh key
    (observed live while wiring this up) - a transient 429 should not fail
    the whole tailoring step."""
    calls = {"n": 0}

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["n"] += 1
        if calls["n"] < 3:
            return _fake_response({"error": "rate limited"}, status_code=429)
        return _fake_response(
            {
                "model": "openai/gpt-oss-120b:free",
                "choices": [{"message": {"content": "Recovered after retry."}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            }
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-oss-120b:free")
    result = provider.complete("hello")

    assert calls["n"] == 3
    assert result.text == "Recovered after retry."


def test_429_exhausting_all_retries_raises_provider_unavailable(monkeypatch) -> None:
    calls = {"n": 0}

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["n"] += 1
        return _fake_response({"error": "rate limited"}, status_code=429)

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-oss-120b:free")
    with pytest.raises(ProviderUnavailableError):
        provider.complete("hello")

    assert calls["n"] == provider_module._MAX_RETRIES + 1
