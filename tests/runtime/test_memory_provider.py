import pytest

from doitall.models.memory import Memory
from doitall.models.message import UserMessage
from doitall.runtime.context import RuntimeContext
from doitall.runtime.memory_provider import MemoryProvider


class FakeMemoryManager:
    def search(
        self,
        query: str,
        limit: int,
    ):
        assert query == "hello"

        return [
            Memory(content="memory 1"),
            Memory(content="memory 2"),
        ]


@pytest.mark.asyncio
async def test_memory_provider():
    provider = MemoryProvider(
        FakeMemoryManager(),
    )

    context = RuntimeContext(
        query="hello",
        messages=[
            UserMessage(content="hello"),
        ],
    )

    await provider.populate(context)

    assert len(context.memories) == 2
    assert context.memories[0].content == "memory 1"
    assert context.memories[1].content == "memory 2"


@pytest.mark.asyncio
async def test_no_messages_but_has_query():
    """When there are no messages but a query is set, memories should be fetched."""

    class AnyQueryManager:
        def search(self, query: str, limit: int):
            return [Memory(content="found")]

    provider = MemoryProvider(AnyQueryManager())

    context = RuntimeContext(query="something")

    await provider.populate(context)

    assert len(context.memories) == 1


@pytest.mark.asyncio
async def test_no_messages_no_query():
    """With empty query and no messages, no search should happen."""
    provider = MemoryProvider(
        FakeMemoryManager(),
    )

    context = RuntimeContext()

    await provider.populate(context)

    assert context.memories == []


@pytest.mark.asyncio
async def test_falls_back_to_last_message_when_no_query():
    """When context.query is empty, fall back to messages[-1].content."""

    class CaptureManager:
        def __init__(self):
            self.called_with = None

        def search(self, query: str, limit: int):
            self.called_with = query
            return []

    manager = CaptureManager()
    provider = MemoryProvider(manager)

    context = RuntimeContext(
        query="",
        messages=[UserMessage(content="last message")],
    )

    await provider.populate(context)

    assert manager.called_with == "last message"
