from unittest.mock import AsyncMock

import pytest

from doitall.agent.executor import AgentExecutor
from doitall.models.message import MessageRole
from doitall.models.provider_response import ProviderResponse
from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_assembler import ContextAssembler
from doitall.runtime.memory_pipeline import MemoryPipeline
from doitall.services.chat_service import ChatService
from doitall.services.conversation_service import ConversationService


class FakeContextAssembler(ContextAssembler):
    def __init__(self, conversation: ConversationService) -> None:
        self._conversation = conversation

    async def assemble(self, query: str, **kwargs: object) -> RuntimeContext:
        return RuntimeContext(
            messages=self._conversation.messages(),
        )


@pytest.mark.asyncio
async def test_chat_service_round_trip():
    conversation = ConversationService()

    assembler = FakeContextAssembler(conversation)

    executor = AsyncMock(spec=AgentExecutor)
    executor.execute.return_value = ProviderResponse(
        content="Hello back!",
        tool_calls=[],
        finish_reason="stop",
        model="test",
    )

    memory_pipeline = AsyncMock(spec=MemoryPipeline)

    service = ChatService(
        conversation_service=conversation,
        context_assembler=assembler,
        agent_executor=executor,
        memory_pipeline=memory_pipeline,
    )

    response = await service.chat("Hello")

    assert response == "Hello back!"

    messages = conversation.messages()

    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert messages[0].content == "Hello"

    assert messages[1].role == MessageRole.ASSISTANT
    assert messages[1].content == "Hello back!"

    memory_pipeline.process.assert_called_once_with(
        messages[0],
        messages[1],
    )


@pytest.mark.asyncio
async def test_chat_service_memory_failure_is_non_fatal():
    """If memory_pipeline.process() raises, the LLM response must still be returned."""
    conversation = ConversationService()
    assembler = FakeContextAssembler(conversation)

    executor = AsyncMock(spec=AgentExecutor)
    executor.execute.return_value = ProviderResponse(
        content="Still works!",
        tool_calls=[],
        finish_reason="stop",
        model="test",
    )

    memory_pipeline = AsyncMock(spec=MemoryPipeline)
    memory_pipeline.process.side_effect = RuntimeError("Qdrant unavailable")

    service = ChatService(
        conversation_service=conversation,
        context_assembler=assembler,
        agent_executor=executor,
        memory_pipeline=memory_pipeline,
    )

    # Must NOT raise — memory failure is swallowed
    response = await service.chat("Hello")

    assert response == "Still works!"


class ToolContextAssembler(ContextAssembler):
    def __init__(self, conversation: ConversationService) -> None:
        self._conversation = conversation

    async def assemble(self, query: str, **kwargs: object) -> RuntimeContext:
        from doitall.models.tool_definition import ToolDefinition

        return RuntimeContext(
            messages=self._conversation.messages(),
            provider=kwargs.get("provider"),
            tools=[
                ToolDefinition(
                    name="calculator",
                    description="Calculate arithmetic",
                    input_schema={"type": "object"},
                )
            ],
        )


@pytest.mark.asyncio
async def test_chat_service_persists_tool_loop_messages():
    from doitall.models.tool_call import ToolCall

    conversation = ConversationService()
    assembler = ToolContextAssembler(conversation)

    executor = AgentExecutor(
        runtime=type("Runtime", (), {})(),
        tool_engine=type("ToolEngine", (), {})(),
        tool_message_builder=type("Builder", (), {})(),
    )

    async def execute(context):
        from doitall.models.message import AssistantMessage, ToolMessage

        context.messages.append(
            AssistantMessage(
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="calculator",
                        arguments={"expression": "2+2"},
                    )
                ]
            )
        )
        context.messages.append(
            ToolMessage(content="4", tool_call_id="call_1", name="calculator")
        )
        return ProviderResponse(content="The answer is 4", model="test")

    executor.execute = AsyncMock(side_effect=execute)
    memory_pipeline = AsyncMock(spec=MemoryPipeline)

    service = ChatService(
        conversation_service=conversation,
        context_assembler=assembler,
        agent_executor=executor,
        memory_pipeline=memory_pipeline,
    )

    response = await service.chat("What is 2+2?")

    assert response == "The answer is 4"
    messages = conversation.messages()
    assert [message.role for message in messages] == [
        MessageRole.USER,
        MessageRole.ASSISTANT,
        MessageRole.TOOL,
        MessageRole.ASSISTANT,
    ]
    assert messages[1].tool_calls[0].name == "calculator"
    assert messages[2].content == "4"
    assert messages[3].content == "The answer is 4"


@pytest.mark.asyncio
async def test_stream_chat_uses_tool_loop_when_tools_are_available():
    conversation = ConversationService()
    assembler = ToolContextAssembler(conversation)

    executor = AsyncMock(spec=AgentExecutor)
    executor.execute.return_value = ProviderResponse(
        content="streamed final", model="test"
    )
    memory_pipeline = AsyncMock(spec=MemoryPipeline)

    service = ChatService(
        conversation_service=conversation,
        context_assembler=assembler,
        agent_executor=executor,
        memory_pipeline=memory_pipeline,
    )

    chunks = [chunk async for chunk in service.stream_chat("Use a tool")]

    assert chunks == ["streamed final"]
    executor.execute.assert_awaited_once()
    assert conversation.messages()[-1].content == "streamed final"
