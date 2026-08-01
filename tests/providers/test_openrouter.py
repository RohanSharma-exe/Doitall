from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.providers.openrouter import OpenrouterProvider


def _make_fake_response(
    content: str = "OpenRouter Working",
    model: str = "openrouter/claude",
    finish_reason: str = "stop",
):
    message = MagicMock()
    message.content = content
    message.tool_calls = []

    choice = MagicMock()
    choice.message = message
    choice.finish_reason = finish_reason

    response = MagicMock()
    response.model = model
    response.choices = [choice]

    return response


@pytest.mark.asyncio
async def test_chat_returns_provider_response():
    provider = OpenrouterProvider()
    fake_response = _make_fake_response()

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}]
        )

    assert isinstance(result, ProviderResponse)
    assert result.content == "OpenRouter Working"
    assert result.finish_reason == "stop"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_chat_content_extracted():
    provider = OpenrouterProvider()
    fake_response = _make_fake_response(content="Routed response")

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(
            messages=[{"role": "user", "content": "Hi"}]
        )

    assert result.content == "Routed response"


@pytest.mark.asyncio
async def test_chat_uses_settings_model():
    """OpenRouter model must come from settings.OPENROUTER_MODEL, not hardcoded."""
    provider = OpenrouterProvider()

    captured = {}

    async def mock_chat(model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(messages=[{"role": "user", "content": "Test"}])

    from doitall.config.settings import settings

    assert captured["model"] == settings.OPENROUTER_MODEL


@pytest.mark.asyncio
async def test_health_check_returns_true():
    """health_check returns True when the LiteLLM client succeeds."""
    provider = OpenrouterProvider()
    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=_make_fake_response(),
    ):
        assert await provider.health_check() is True


@pytest.mark.asyncio
async def test_health_check_returns_false_on_error():
    """health_check returns False when the LiteLLM client raises."""
    provider = OpenrouterProvider()
    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        side_effect=Exception("auth error"),
    ):
        assert await provider.health_check() is False


def test_parse_tool_calls_empty():
    provider = OpenrouterProvider()
    message = MagicMock()
    message.tool_calls = []
    assert provider._parse_tool_calls(message) == []
