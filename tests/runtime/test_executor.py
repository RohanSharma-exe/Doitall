from unittest.mock import AsyncMock, Mock

import pytest

from doitall.agent.agent import Agent
from doitall.agent.manager import AgentManager
from doitall.models.message import UserMessage
from doitall.providers.manager import ProviderManager
from doitall.runtime.context import RuntimeContext
from doitall.runtime.executor import RuntimeExecutor
from doitall.runtime.prompt_builder import PromptBuilder


def create_executor():
    provider = AsyncMock()
    provider.chat.return_value = "OK"

    provider_manager = Mock(spec=ProviderManager)
    provider_manager.default.return_value = provider

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
