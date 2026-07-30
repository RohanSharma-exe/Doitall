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

    async def assemble(self, query: str) -> RuntimeContext:
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
