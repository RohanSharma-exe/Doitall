from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.providers.anthropic import AnthropicProvider


def _make_fake_response(
    content: str = "Anthropic Working",
    model: str = "claude-3-5-sonnet",
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
    provider = AnthropicProvider()
    fake_response = _make_fake_response()

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(messages=[{"role": "user", "content": "Hello"}])

    assert isinstance(result, ProviderResponse)
    assert result.content == "Anthropic Working"
    assert result.finish_reason == "stop"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_chat_content_extracted():
    provider = AnthropicProvider()
    fake_response = _make_fake_response(content="Hello from Anthropic")

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(messages=[{"role": "user", "content": "Hi"}])

    assert result.content == "Hello from Anthropic"


@pytest.mark.asyncio
async def test_chat_uses_settings_model():
    """Verify model is read from settings.ANTHROPIC_MODEL, not hardcoded."""
    provider = AnthropicProvider()

    captured = {}

    async def mock_chat(model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(messages=[{"role": "user", "content": "Test"}])

    from doitall.config.settings import settings

    assert captured["model"] == settings.ANTHROPIC_MODEL


@pytest.mark.asyncio
async def test_health_check_returns_true():
    """health_check returns True when the LiteLLM client succeeds."""
    provider = AnthropicProvider()
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
    provider = AnthropicProvider()
    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        side_effect=Exception("auth error"),
    ):
        assert await provider.health_check() is False


def test_convert_tools():
    from doitall.models.tool_definition import ToolDefinition

    provider = AnthropicProvider()

    tools = [
        ToolDefinition(
            name="calculator",
            description="Do math",
            input_schema={
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        )
    ]

    converted = provider._convert_tools(tools)

    assert converted[0]["type"] == "function"
    assert converted[0]["function"]["name"] == "calculator"


def test_parse_tool_calls_empty():
    provider = AnthropicProvider()
    message = MagicMock()
    message.tool_calls = []
    assert provider._parse_tool_calls(message) == []


def test_parse_tool_calls_with_call():
    import json

    provider = AnthropicProvider()

    fn = MagicMock()
    fn.name = "calculator"
    fn.arguments = json.dumps({"expression": "1+1"})

    call = MagicMock()
    call.id = "call_xyz"
    call.function = fn

    message = MagicMock()
    message.tool_calls = [call]

    result = provider._parse_tool_calls(message)
    assert len(result) == 1
    assert result[0].name == "calculator"
    assert result[0].arguments == {"expression": "1+1"}
