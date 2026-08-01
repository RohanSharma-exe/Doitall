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
        memory_filter=MemoryFilter(min_length=5, max_length=10000),
        scorer=MemoryScorer(base_score=0.5),
    )


@pytest.mark.asyncio
async def test_pipeline():
    store = InMemoryStore()

    pipeline = _make_pipeline(store)

    await pipeline.process(
        UserMessage(content="Hello"),
        AssistantMessage(content="Hi"),
    )

    memories = await store.get_all()

    assert len(memories) == 1
    assert memories[0].content == ("User preference/fact: Hello\nAssistant outcome: Hi")
    # The scorer now calculates importance based on content
    assert memories[0].importance >= 0.0
    assert memories[0].importance <= 1.0


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
        scorer=MemoryScorer(base_score=0.5),
    )

    await pipeline.process(
        UserMessage(content="Hello"),
        AssistantMessage(content="Hi"),
    )

    memories = await store.get_all()
    assert memories == []


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

    assert await store.count() == 2
