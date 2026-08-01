import pytest
from unittest.mock import AsyncMock, Mock

from doitall.memory.vector_memory_store import VectorMemoryStore
from doitall.models.memory import Memory


def _make_async_repository() -> Mock:
    repo = Mock()
    repo.save = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.search = AsyncMock(return_value=[])
    repo.delete = AsyncMock()
    repo.count = AsyncMock(return_value=0)
    repo.clear = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_add_calls_repository():
    repository = _make_async_repository()

    store = VectorMemoryStore(repository)

    memory = Memory(content="Python is awesome.")

    await store.add(memory)

    repository.save.assert_called_once_with(memory)


@pytest.mark.asyncio
async def test_clear_calls_repository():
    repository = _make_async_repository()

    store = VectorMemoryStore(repository)

    await store.clear()

    repository.clear.assert_called_once()


@pytest.mark.asyncio
async def test_count_calls_repository():
    repository = _make_async_repository()
    repository.count = AsyncMock(return_value=5)

    store = VectorMemoryStore(repository)

    assert await store.count() == 5
