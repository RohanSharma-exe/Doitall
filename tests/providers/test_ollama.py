from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.providers.ollama import OllamaProvider


def _make_fake_response(
    content: str = "Ollama Working",
    model: str = "llama3.2",
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
    provider = OllamaProvider()
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
    assert result.content == "Ollama Working"
    assert result.finish_reason == "stop"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_chat_content_extracted():
    provider = OllamaProvider()
    fake_response = _make_fake_response(content="Local model response")

    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=fake_response,
    ):
        result = await provider.chat(
            messages=[{"role": "user", "content": "Hi"}]
        )

    assert result.content == "Local model response"


@pytest.mark.asyncio
async def test_chat_uses_settings_model():
    """Ollama model must come from settings.OLLAMA_MODEL."""
    provider = OllamaProvider()

    captured = {}

    async def mock_chat(model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(messages=[{"role": "user", "content": "Test"}])

    from doitall.config.settings import settings

    assert captured["model"] == settings.OLLAMA_MODEL


@pytest.mark.asyncio
async def test_health_check_returns_true():
    provider = OllamaProvider()
    assert await provider.health_check() is True


def test_convert_tools():
    from doitall.models.tool_definition import ToolDefinition

    provider = OllamaProvider()

    tools = [
        ToolDefinition(
            name="list_files",
            description="List files in directory",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        )
    ]

    converted = provider._convert_tools(tools)
    assert converted[0]["function"]["name"] == "list_files"


def test_parse_tool_calls_empty():
    provider = OllamaProvider()
    message = MagicMock()
    message.tool_calls = []
    assert provider._parse_tool_calls(message) == []
