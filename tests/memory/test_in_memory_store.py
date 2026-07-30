import pytest

from doitall.memory.in_memory_store import InMemoryStore
from doitall.models.memory import Memory


@pytest.fixture
def store() -> InMemoryStore:
    return InMemoryStore()


def test_add_memory(store: InMemoryStore) -> None:
    memory = Memory(content="Hello World")

    store.add(memory)

    memories = store.get_all()

    assert len(memories) == 1
    assert memories[0] == memory


def test_get_all_returns_copy(store: InMemoryStore) -> None:
    memory = Memory(content="Test Memory")

    store.add(memory)

    memories = store.get_all()

    memories.append(Memory(content="Another"))

    assert store.count() == 1
    assert len(store.get_all()) == 1


def test_clear(store: InMemoryStore) -> None:
    store.add(Memory(content="One"))
    store.add(Memory(content="Two"))

    assert store.count() == 2

    store.clear()

    assert store.count() == 0
    assert store.get_all() == []


def test_count_empty(store: InMemoryStore) -> None:
    assert store.count() == 0


def test_count_after_add(store: InMemoryStore) -> None:
    store.add(Memory(content="A"))
    store.add(Memory(content="B"))
    store.add(Memory(content="C"))

    assert store.count() == 3


def test_multiple_memories(store: InMemoryStore) -> None:
    memories = [
        Memory(content="Memory 1"),
        Memory(content="Memory 2"),
        Memory(content="Memory 3"),
    ]

    for memory in memories:
        store.add(memory)

    result = store.get_all()

    assert result == memories


def test_clear_empty_store(store: InMemoryStore) -> None:
    store.clear()

    assert store.count() == 0
    assert store.get_all() == []


def test_add_duplicate_memory_instances(store: InMemoryStore) -> None:
    memory = Memory(content="Duplicate")

    store.add(memory)
    store.add(memory)

    assert store.count() == 2


def test_modifying_returned_list_does_not_modify_store(
    store: InMemoryStore,
) -> None:
    store.add(Memory(content="One"))

    result = store.get_all()

    result.clear()

    assert store.count() == 1
    assert len(store.get_all()) == 1
