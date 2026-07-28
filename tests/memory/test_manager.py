from doitall.memory.in_memory_store import InMemoryStore
from doitall.memory.manager import MemoryManager
from doitall.models.memory import Memory


def test_add_memory():
    manager = MemoryManager(
        store=InMemoryStore(),
    )

    manager.add(Memory(content="User likes Python."))

    assert manager.count() == 1
    assert manager.all()[0].content == "User likes Python."


def test_clear_memory():
    manager = MemoryManager(
        store=InMemoryStore(),
    )

    manager.add(Memory(content="Memory 1"))

    manager.add(Memory(content="Memory 2"))

    assert manager.count() == 2

    manager.clear()

    assert manager.count() == 0
    assert manager.all() == []
