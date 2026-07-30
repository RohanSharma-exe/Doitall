import pytest

from doitall.memory.in_memory_store import InMemoryStore
from doitall.models.memory import Memory


@pytest.fixture
def store() -> InMemoryStore:
    return InMemoryStore()


@pytest.mark.asyncio
async def test_add_memory(store: InMemoryStore) -> None:
    memory = Memory(content="Hello World")

    await store.add(memory)

    memories = await store.get_all()

    assert len(memories) == 1
    assert memories[0] == memory


@pytest.mark.asyncio
async def test_get_all_returns_copy(store: InMemoryStore) -> None:
    memory = Memory(content="Test Memory")

    await store.add(memory)

    memories = await store.get_all()

    memories.append(Memory(content="Another"))

    assert store.count() == 1
    assert len(await store.get_all()) == 1


@pytest.mark.asyncio
async def test_clear(store: InMemoryStore) -> None:
    await store.add(Memory(content="One"))
    await store.add(Memory(content="Two"))

    assert store.count() == 2

    store.clear()

    assert store.count() == 0
    assert await store.get_all() == []


def test_count_empty(store: InMemoryStore) -> None:
    assert store.count() == 0


@pytest.mark.asyncio
async def test_count_after_add(store: InMemoryStore) -> None:
    await store.add(Memory(content="A"))
    await store.add(Memory(content="B"))
    await store.add(Memory(content="C"))

    assert store.count() == 3


@pytest.mark.asyncio
async def test_multiple_memories(store: InMemoryStore) -> None:
    memories = [
        Memory(content="Memory 1"),
        Memory(content="Memory 2"),
        Memory(content="Memory 3"),
    ]

    for memory in memories:
        await store.add(memory)

    result = await store.get_all()

    assert result == memories


@pytest.mark.asyncio
async def test_clear_empty_store(store: InMemoryStore) -> None:
    store.clear()

    assert store.count() == 0
    assert await store.get_all() == []


@pytest.mark.asyncio
async def test_add_duplicate_memory_instances(store: InMemoryStore) -> None:
    memory = Memory(content="Duplicate")

    await store.add(memory)
    await store.add(memory)

    assert store.count() == 2


@pytest.mark.asyncio
async def test_modifying_returned_list_does_not_modify_store(
    store: InMemoryStore,
) -> None:
    await store.add(Memory(content="One"))

    result = await store.get_all()

    result.clear()

    assert store.count() == 1
    assert len(await store.get_all()) == 1
