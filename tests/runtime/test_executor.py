from unittest.mock import AsyncMock, Mock

import pytest

from doitall.agent.agent import Agent
from doitall.agent.manager import AgentManager
from doitall.models.message import ToolMessage, UserMessage
from doitall.models.tool_call import ToolExecutionMetadata
from doitall.providers.manager import ProviderCandidate, ProviderManager
from doitall.runtime.context import RuntimeContext
from doitall.runtime.executor import RuntimeExecutor
from doitall.runtime.prompt_builder import PromptBuilder


def create_executor():
    provider = AsyncMock()
    provider.chat.return_value = "OK"

    provider.name = "default"
    provider_manager = Mock(spec=ProviderManager)
    provider_manager.default.return_value = provider
    provider_manager.fallback_candidates.return_value = [ProviderCandidate(provider)]

    builder = PromptBuilder(
        AgentManager(
            Agent(
                name="Assistant",
                system_prompt="System",
            )
        )
    )

    return (
        RuntimeExecutor(
            builder,
            provider_manager,
        ),
        provider,
    )


def test_executor_prepare():
    executor, _ = create_executor()

    context = RuntimeContext(
        messages=[
            UserMessage(content="Hello"),
        ]
    )

    messages = executor.prepare(context)

    assert len(messages) == 2
    assert messages[0].content == "System"
    assert messages[1].content == "Hello"


def test_executor_empty_context():
    executor, _ = create_executor()

    messages = executor.prepare(RuntimeContext())

    assert len(messages) == 1
    assert messages[0].content == "System"


def test_prepare_returns_new_list():
    executor, _ = create_executor()

    context = RuntimeContext()

    first = executor.prepare(context)
    second = executor.prepare(context)

    assert first is not second


def test_prepare_does_not_modify_context():
    executor, _ = create_executor()

    context = RuntimeContext(
        messages=[
            UserMessage(content="Hello"),
        ]
    )

    executor.prepare(context)

    assert len(context.messages) == 1


@pytest.mark.asyncio
async def test_execute():
    executor, _ = create_executor()

    response = await executor.execute(RuntimeContext())

    assert response == "OK"


@pytest.mark.asyncio
async def test_execute_uses_provider_override():
    executor, _ = create_executor()

    override_provider = AsyncMock()
    override_provider.chat.return_value = "OVERRIDE"
    override_provider.name = "groq"
    executor._provider_manager.get.return_value = override_provider
    executor._provider_manager.fallback_candidates.return_value = [
        ProviderCandidate(override_provider)
    ]

    response = await executor.execute(RuntimeContext(provider="groq"))

    assert response == "OVERRIDE"
    executor._provider_manager.fallback_candidates.assert_called_once_with("groq")
    executor._provider_manager.default.assert_not_called()


@pytest.mark.asyncio
async def test_provider_called_once():
    executor, provider = create_executor()

    await executor.execute(RuntimeContext())

    provider.chat.assert_called_once()


@pytest.mark.asyncio
async def test_execute_sends_prepared_messages():
    executor, provider = create_executor()

    await executor.execute(RuntimeContext())

    payload = provider.chat.call_args.args[0]

    assert payload[0]["role"] == "system"
    assert payload[0]["content"] == "System"


@pytest.mark.asyncio
async def test_execute_does_not_modify_context():
    executor, _ = create_executor()

    context = RuntimeContext()

    await executor.execute(context)

    assert context.messages == []
    assert context.memories == []
    assert context.knowledge == []


@pytest.mark.asyncio
async def test_execute_falls_back_to_next_provider():
    first_provider = AsyncMock()
    first_provider.name = "first"
    first_provider.chat.side_effect = RuntimeError("first failed")

    second_provider = AsyncMock()
    second_provider.name = "second"
    second_provider.chat.return_value = "OK"

    manager = ProviderManager()
    manager.register(first_provider, default=True)
    manager.register(second_provider)

    builder = PromptBuilder(
        AgentManager(Agent(name="Assistant", system_prompt="System"))
    )
    executor = RuntimeExecutor(builder, manager)

    response = await executor.execute(RuntimeContext())

    assert response == "OK"
    first_provider.chat.assert_called_once()
    second_provider.chat.assert_called_once()


@pytest.mark.asyncio
async def test_execute_prefers_provider_override_then_fallback():
    default_provider = AsyncMock()
    default_provider.name = "default"
    default_provider.chat.return_value = "DEFAULT"

    override_provider = AsyncMock()
    override_provider.name = "override"
    override_provider.chat.side_effect = RuntimeError("override failed")

    manager = ProviderManager()
    manager.register(default_provider, default=True)
    manager.register(override_provider)

    builder = PromptBuilder(
        AgentManager(Agent(name="Assistant", system_prompt="System"))
    )
    executor = RuntimeExecutor(builder, manager)

    response = await executor.execute(RuntimeContext(provider="override"))

    assert response == "DEFAULT"
    override_provider.chat.assert_called_once()
    default_provider.chat.assert_called_once()


def test_payload_does_not_expose_tool_execution_metadata() -> None:
    executor, _ = create_executor()

    metadata = ToolExecutionMetadata(
        status="success",
        duration_ms=12.5,
    )

    messages = [
        ToolMessage(
            content="42",
            tool_call_id="call-1",
            name="calculator",
            execution_metadata=metadata,
        ),
    ]

    payload = executor._payload(messages)

    assert len(payload) == 1
    assert payload[0]["role"] == "tool"
    assert payload[0]["content"] == "42"
    assert payload[0]["tool_call_id"] == "call-1"
    assert payload[0]["name"] == "calculator"

    assert "execution_metadata" not in payload[0]
