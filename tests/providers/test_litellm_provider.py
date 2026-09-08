"""Tests for the generic LiteLLMProvider."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from doitall.config.settings import settings
from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_definition import ToolDefinition
from doitall.providers.litellm_provider import LiteLLMProvider


def _make_fake_response(
    content: str = "Hello",
    model: str = "gpt-4o",
    finish_reason: str = "stop",
) -> MagicMock:
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


def _make_provider(name: str = "openai", model: str = "gpt-4o") -> LiteLLMProvider:
    return LiteLLMProvider(name, model)


# ---------------------------------------------------------------------------
# chat()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_returns_provider_response():
    provider = _make_provider()
    fake = _make_fake_response()

    with patch.object(provider.client, "chat", new_callable=AsyncMock, return_value=fake):
        result = await provider.chat(messages=[{"role": "user", "content": "Hello"}])

    assert isinstance(result, ProviderResponse)
    assert result.content == "Hello"
    assert result.finish_reason == "stop"
    assert result.tool_calls == []


@pytest.mark.asyncio
async def test_chat_uses_default_model():
    provider = _make_provider(model="gpt-4o")
    captured: dict = {}

    async def mock_chat(*, model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(messages=[{"role": "user", "content": "Test"}])

    assert captured["model"] == "gpt-4o"


@pytest.mark.asyncio
async def test_chat_model_kwarg_overrides_default():
    provider = _make_provider(model="gpt-4o")
    captured: dict = {}

    async def mock_chat(*, model, messages, **kwargs):
        captured["model"] = model
        return _make_fake_response(model=model)

    with patch.object(provider.client, "chat", side_effect=mock_chat):
        await provider.chat(
            messages=[{"role": "user", "content": "Test"}],
            model="gpt-4-turbo",
        )

    assert captured["model"] == "gpt-4-turbo"


@pytest.mark.asyncio
async def test_chat_content_extracted():
    provider = _make_provider()
    fake = _make_fake_response(content="Hello from LiteLLM")

    with patch.object(provider.client, "chat", new_callable=AsyncMock, return_value=fake):
        result = await provider.chat(messages=[{"role": "user", "content": "Hi"}])

    assert result.content == "Hello from LiteLLM"


# ---------------------------------------------------------------------------
# health_check()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check_returns_true_when_client_succeeds():
    provider = _make_provider()
    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        return_value=_make_fake_response(),
    ):
        assert await provider.health_check() is True


@pytest.mark.asyncio
async def test_health_check_returns_false_on_error():
    provider = _make_provider()
    with patch.object(
        provider.client,
        "chat",
        new_callable=AsyncMock,
        side_effect=Exception("auth error"),
    ):
        assert await provider.health_check() is False


@pytest.mark.asyncio
async def test_health_check_custom_fn_used():
    async def always_true() -> bool:
        return True

    provider = LiteLLMProvider("custom", "model", health_check_fn=always_true)
    assert await provider.health_check() is True


@pytest.mark.asyncio
async def test_health_check_custom_fn_failure():
    async def always_false() -> bool:
        return False

    provider = LiteLLMProvider("custom", "model", health_check_fn=always_false)
    assert await provider.health_check() is False


# ---------------------------------------------------------------------------
# Tool conversion & parsing (inherited from BaseProvider)
# ---------------------------------------------------------------------------


def test_convert_tools():
    provider = _make_provider()
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
    assert converted[0]["function"]["description"] == "Do math"


def test_parse_tool_calls_empty():
    provider = _make_provider()
    message = MagicMock()
    message.tool_calls = []
    assert provider._parse_tool_calls(message) == []


def test_parse_tool_calls_with_call():
    provider = _make_provider()

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


# ---------------------------------------------------------------------------
# Provider name
# ---------------------------------------------------------------------------


def test_provider_name():
    provider = LiteLLMProvider("anthropic", "claude-3-5-sonnet")
    assert provider.name == "anthropic"


@pytest.mark.parametrize(
    "name,model",
    [
        ("gemini", settings.GEMINI_MODEL),
        ("groq", settings.GROQ_MODEL),
        ("openai", settings.OPENAI_MODEL),
        ("anthropic", settings.ANTHROPIC_MODEL),
        ("nvidia", settings.NVIDIA_MODEL),
        ("ollama", settings.OLLAMA_MODEL),
        ("openrouter", settings.OPENROUTER_MODEL),
    ],
)
def test_all_provider_names_and_models(name: str, model: str):
    provider = LiteLLMProvider(name, model)
    assert provider.name == name
    assert provider._default_model == model
