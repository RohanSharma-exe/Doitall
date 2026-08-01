from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.providers.openai import OpenAIProvider


def _make_fake_response(
    content: str = "OpenAI Working",
    model: str = "gpt-4o",
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
    provider = OpenAIProvider()
    fake_response = _make_fake_response()

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(messages=[{"role": "user", "content": "Hello"}])

    assert isinstance(result, ProviderResponse)
    assert result.content == "OpenAI Working"
    assert result.finish_reason == "stop"
    assert result.model == "gpt-4o"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_chat_content_extracted():
    provider = OpenAIProvider()
    fake_response = _make_fake_response(content="Hello from OpenAI")

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(messages=[{"role": "user", "content": "Hi"}])

    assert result.content == "Hello from OpenAI"


@pytest.mark.asyncio
async def test_chat_uses_settings_model():
    """Verify no hardcoded model string — model is read from settings."""
    provider = OpenAIProvider()

    captured = {}

    async def mock_chat(model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(messages=[{"role": "user", "content": "Test"}])

    from doitall.config.settings import settings

    assert captured["model"] == settings.OPENAI_MODEL


@pytest.mark.asyncio
async def test_health_check_returns_true():
    """health_check returns True when the LiteLLM client succeeds."""
    provider = OpenAIProvider()
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
    provider = OpenAIProvider()
    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        side_effect=Exception("auth error"),
    ):
        assert await provider.health_check() is False


def test_convert_tools():
    from doitall.models.tool_definition import ToolDefinition

    provider = OpenAIProvider()

    tools = [
        ToolDefinition(
            name="search",
            description="Search the web",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )
    ]

    converted = provider._convert_tools(tools)

    assert converted == [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        }
    ]


def test_parse_tool_calls_empty():
    provider = OpenAIProvider()
    message = MagicMock()
    message.tool_calls = []
    assert provider._parse_tool_calls(message) == []


def test_parse_tool_calls_with_call():
    import json

    provider = OpenAIProvider()

    fn = MagicMock()
    fn.name = "search"
    fn.arguments = json.dumps({"query": "doitall"})

    call = MagicMock()
    call.id = "call_abc"
    call.function = fn

    message = MagicMock()
    message.tool_calls = [call]

    result = provider._parse_tool_calls(message)
    assert len(result) == 1
    assert result[0].id == "call_abc"
    assert result[0].name == "search"
    assert result[0].arguments == {"query": "doitall"}


def test_parse_tool_calls_accepts_dict_arguments():
    provider = OpenAIProvider()

    fn = MagicMock()
    fn.name = "search"
    fn.arguments = {"query": "doitall"}

    call = MagicMock()
    call.id = "call_dict"
    call.function = fn

    message = MagicMock()
    message.tool_calls = [call]

    result = provider._parse_tool_calls(message)

    assert result[0].arguments == {"query": "doitall"}


def test_parse_tool_calls_rejects_malformed_json():
    from doitall.providers.exceptions import ProviderResponseError

    provider = OpenAIProvider()

    fn = MagicMock()
    fn.name = "search"
    fn.arguments = "{not-json"

    call = MagicMock()
    call.id = "call_bad"
    call.function = fn

    message = MagicMock()
    message.tool_calls = [call]

    with pytest.raises(ProviderResponseError, match="not valid JSON"):
        provider._parse_tool_calls(message)
