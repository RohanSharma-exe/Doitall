import pytest

from doitall.memory.in_memory_store import InMemoryStore
from doitall.memory.manager import MemoryManager
from doitall.models.message import AssistantMessage, UserMessage
from doitall.runtime.memory_extractor import MemoryExtractor
from doitall.runtime.memory_filter import MemoryFilter
from doitall.runtime.memory_pipeline import MemoryPipeline
from doitall.runtime.memory_scorer import MemoryScorer


def _make_pipeline(store: InMemoryStore) -> MemoryPipeline:
    return MemoryPipeline(
        manager=MemoryManager(store),
        extractor=MemoryExtractor(),
        memory_filter=MemoryFilter(),
        scorer=MemoryScorer(),
    )


@pytest.mark.asyncio
async def test_pipeline():
    store = InMemoryStore()

    pipeline = _make_pipeline(store)

    await pipeline.process(
        UserMessage(content="Hello"),
        AssistantMessage(content="Hi"),
    )

    memories = store.get_all()

    assert len(memories) == 1
    assert memories[0].content == ("User: Hello\nAssistant: Hi")
    assert memories[0].importance == 0.5


@pytest.mark.asyncio
async def test_pipeline_filtered_memories_not_stored():
    """Memories rejected by MemoryFilter must not be added to the store."""

    class RejectAllFilter:
        def allow(self, memory) -> bool:
            return False

    store = InMemoryStore()
    pipeline = MemoryPipeline(
        manager=MemoryManager(store),
        extractor=MemoryExtractor(),
        memory_filter=RejectAllFilter(),
        scorer=MemoryScorer(),
    )

    await pipeline.process(
        UserMessage(content="Hello"),
        AssistantMessage(content="Hi"),
    )

    assert store.get_all() == []


@pytest.mark.asyncio
async def test_pipeline_multiple_turns():
    store = InMemoryStore()
    pipeline = _make_pipeline(store)

    await pipeline.process(
        UserMessage(content="Turn one"),
        AssistantMessage(content="Response one"),
    )

    await pipeline.process(
        UserMessage(content="Turn two"),
        AssistantMessage(content="Response two"),
    )

    assert store.count() == 2
