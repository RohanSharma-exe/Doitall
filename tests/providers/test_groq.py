from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.providers.groq import GroqProvider


def _make_fake_litellm_response(
    content: str = "Groq Working",
    model: str = "groq-test",
    finish_reason: str = "stop",
):
    """Build a fake LiteLLM-style response object."""
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
    provider = GroqProvider()

    fake_response = _make_fake_litellm_response()

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
    assert result.content == "Groq Working"
    assert result.finish_reason == "stop"
    assert result.model == "groq-test"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_chat_content_extracted():
    provider = GroqProvider()

    fake_response = _make_fake_litellm_response(content="Hello from Groq")

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(
            messages=[{"role": "user", "content": "Hi"}]
        )

    assert result.content == "Hello from Groq"


@pytest.mark.asyncio
async def test_health_check_returns_true():
    provider = GroqProvider()
    assert await provider.health_check() is True


def test_convert_tools():
    from doitall.models.tool_definition import ToolDefinition

    provider = GroqProvider()

    tools = [
        ToolDefinition(
            name="calculator",
            description="Calculator",
            input_schema={
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        )
    ]

    converted = provider._convert_tools(tools)

    assert converted == [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Calculator",
                "parameters": {
                    "type": "object",
                    "properties": {"expression": {"type": "string"}},
                    "required": ["expression"],
                },
            },
        }
    ]


def test_parse_tool_calls_empty():
    provider = GroqProvider()

    message = MagicMock()
    message.tool_calls = []

    assert provider._parse_tool_calls(message) == []


def test_parse_tool_calls_with_call():
    import json

    provider = GroqProvider()

    fn = MagicMock()
    fn.name = "calculator"
    fn.arguments = json.dumps({"expression": "2+2"})

    call = MagicMock()
    call.id = "call_1"
    call.function = fn

    message = MagicMock()
    message.tool_calls = [call]

    result = provider._parse_tool_calls(message)

    assert len(result) == 1
    assert result[0].id == "call_1"
    assert result[0].name == "calculator"
    assert result[0].arguments == {"expression": "2+2"}
