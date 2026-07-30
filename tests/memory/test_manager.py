from doitall.memory.in_memory_store import InMemoryStore
from doitall.memory.manager import MemoryManager
from doitall.models.memory import Memory


def test_add_memory():
    manager = MemoryManager(
        InMemoryStore(),
    )

    manager.add(
        Memory(content="Hello"),
    )

    assert manager.count() == 1


def test_clear():
    manager = MemoryManager(
        InMemoryStore(),
    )

    manager.add(
        Memory(content="One"),
    )

    manager.clear()

    assert manager.count() == 0


def test_search_falls_back_to_recent_memories():
    manager = MemoryManager(
        InMemoryStore(),
    )

    manager.add(Memory(content="One"))
    manager.add(Memory(content="Two"))
    manager.add(Memory(content="Three"))

    memories = manager.search(
        "ignored",
        limit=2,
    )

    assert len(memories) == 2
    assert memories[0].content == "Two"
    assert memories[1].content == "Three"
