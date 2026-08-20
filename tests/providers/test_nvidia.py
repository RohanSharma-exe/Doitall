"""Tests for the NVIDIA NIM provider adapter."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.providers.nvidia import NvidiaProvider


def _make_fake_response(
    content: str = "NVIDIA response",
    model: str = "nvidia/llama-3.3-nemotron-super-49b-v1",
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
    response.usage = None

    return response


@pytest.mark.asyncio
async def test_chat_returns_provider_response():
    """chat() wraps the LiteLLM response into a ProviderResponse."""
    provider = NvidiaProvider()
    fake_response = _make_fake_response()

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(messages=[{"role": "user", "content": "Hello"}])

    assert isinstance(result, ProviderResponse)
    assert result.content == "NVIDIA response"
    assert result.finish_reason == "stop"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_chat_content_extracted():
    """content field is correctly extracted from the LiteLLM response message."""
    provider = NvidiaProvider()
    fake_response = _make_fake_response(content="NIM is fast")

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(messages=[{"role": "user", "content": "Hi"}])

    assert result.content == "NIM is fast"


@pytest.mark.asyncio
async def test_chat_uses_settings_model():
    """chat() falls back to settings.NVIDIA_MODEL when no model is provided."""
    provider = NvidiaProvider()
    captured: dict = {}

    async def mock_chat(model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(messages=[{"role": "user", "content": "Test"}])

    from doitall.config.settings import settings

    assert captured["model"] == settings.NVIDIA_MODEL


@pytest.mark.asyncio
async def test_chat_model_override():
    """Callers can override the model via the model= kwarg."""
    provider = NvidiaProvider()
    captured: dict = {}

    async def mock_chat(model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(
            messages=[{"role": "user", "content": "Test"}],
            model="nvidia/llama-3.1-405b-instruct",
        )

    assert captured["model"] == "nvidia/llama-3.1-405b-instruct"


@pytest.mark.asyncio
async def test_stream_yields_chunks():
    """stream() yields text chunks from the LiteLLM stream client."""
    provider = NvidiaProvider()

    async def fake_stream(model, messages, **kwargs):
        for chunk in ["hello", " world"]:
            yield chunk

    with patch.object(provider.client, "stream", side_effect=fake_stream):
        chunks = []
        async for chunk in provider.stream(
            messages=[{"role": "user", "content": "Stream me"}]
        ):
            chunks.append(chunk)

    assert chunks == ["hello", " world"]


@pytest.mark.asyncio
async def test_health_check_returns_true():
    """health_check returns True when the LiteLLM client succeeds."""
    provider = NvidiaProvider()
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
    provider = NvidiaProvider()
    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        side_effect=Exception("auth error"),
    ):
        assert await provider.health_check() is False


def test_parse_tool_calls_empty():
    """_parse_tool_calls returns an empty list when no tool calls are present."""
    provider = NvidiaProvider()
    message = MagicMock()
    message.tool_calls = []
    assert provider._parse_tool_calls(message) == []


def test_provider_name():
    """Provider name must be 'nvidia' for routing and registry lookup."""
    assert NvidiaProvider().name == "nvidia"


@pytest.mark.asyncio
async def test_usage_tokens_extracted():
    """Usage token counts are extracted and normalized."""
    provider = NvidiaProvider()

    fake_response = _make_fake_response()
    usage = MagicMock()
    usage.prompt_tokens = 10
    usage.completion_tokens = 20
    usage.total_tokens = 30
    fake_response.usage = usage

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(messages=[{"role": "user", "content": "usage test"}])

    assert result.usage_tokens == {"prompt": 10, "completion": 20, "total": 30}
