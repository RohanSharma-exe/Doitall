import pytest

from doitall.core.exceptions import ValidationError
from doitall.memory.in_memory_store import InMemoryStore
from doitall.memory.manager import MemoryManager
from doitall.models.memory import Memory


def _manager() -> MemoryManager:
    return MemoryManager(InMemoryStore())


@pytest.mark.asyncio
async def test_add_and_retrieve_all():
    manager = _manager()
    memory = Memory(content="Remember this")
    await manager.add(memory)

    all_memories = await manager.all()
    assert len(all_memories) == 1
    assert all_memories[0].content == "Remember this"


@pytest.mark.asyncio
async def test_add_empty_content_raises_validation_error():
    manager = _manager()
    with pytest.raises(ValidationError):
        await manager.add(Memory(content=""))


@pytest.mark.asyncio
async def test_add_whitespace_only_raises_validation_error():
    manager = _manager()
    with pytest.raises(ValidationError):
        await manager.add(Memory(content="   "))


@pytest.mark.asyncio
async def test_search_empty_query_returns_empty():
    manager = _manager()
    await manager.add(Memory(content="Some memory"))

    result = await manager.search(query="")
    assert result == []


@pytest.mark.asyncio
async def test_search_whitespace_query_returns_empty():
    manager = _manager()
    await manager.add(Memory(content="Some memory"))

    result = await manager.search(query="   ")
    assert result == []


@pytest.mark.asyncio
async def test_search_falls_back_to_recent_when_store_has_no_semantic_search():
    """InMemoryStore raises NotImplementedError for search() — manager should fall back."""
    manager = _manager()
    for i in range(10):
        await manager.add(Memory(content=f"Memory {i}"))

    result = await manager.search(query="something", limit=3)
    # Falls back to last 3 from get_all()
    assert len(result) == 3
    assert result[-1].content == "Memory 9"


@pytest.mark.asyncio
async def test_all_returns_copy():
    """all() must return a copy — mutations must not affect the store."""
    manager = _manager()
    await manager.add(Memory(content="Keep this"))

    memories = await manager.all()
    memories.clear()

    assert len(await manager.all()) == 1


@pytest.mark.asyncio
async def test_count_zero_initially():
    manager = _manager()
    assert await manager.count() == 0


@pytest.mark.asyncio
async def test_count_increments():
    manager = _manager()
    await manager.add(Memory(content="One"))
    await manager.add(Memory(content="Two"))
    assert await manager.count() == 2


@pytest.mark.asyncio
async def test_clear_empties_store():
    manager = _manager()
    await manager.add(Memory(content="To be cleared"))
    await manager.clear()
    assert await manager.count() == 0
