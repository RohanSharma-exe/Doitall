from unittest.mock import Mock

from doitall.memory.vector_memory_store import VectorMemoryStore
from doitall.models.memory import Memory


def test_add_calls_repository():
    repository = Mock()

    store = VectorMemoryStore(repository)

    memory = Memory(content="Python is awesome.")

    store.add(memory)

    repository.save.assert_called_once_with(memory)


def test_clear_calls_repository():
    repository = Mock()

    store = VectorMemoryStore(repository)

    store.clear()

    repository.clear.assert_called_once()


def test_count_calls_repository():
    repository = Mock()
    repository.count.return_value = 5

    store = VectorMemoryStore(repository)

    assert store.count() == 5
