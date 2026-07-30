import pytest
from unittest.mock import AsyncMock, Mock

from doitall.memory.qdrant_repository import QdrantRepository
from doitall.models.memory import Memory


def test_repository_creation():
    vector_store = Mock()
    embedding_manager = Mock()

    repository = QdrantRepository(
        vector_store=vector_store,
        embedding_manager=embedding_manager,
    )

    assert repository.vector_store is vector_store
    assert repository.embedding_manager is embedding_manager


@pytest.mark.asyncio
async def test_save_memory():
    vector_store = Mock()

    embedding_manager = Mock()
    embedding_manager.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])

    repository = QdrantRepository(
        vector_store=vector_store,
        embedding_manager=embedding_manager,
    )

    memory = Memory(content="Python is awesome.")

    await repository.save(memory)

    embedding_manager.embed.assert_called_once_with("Python is awesome.")

    vector_store.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_search_memory():
    vector_store = Mock()

    vector_store.search.return_value = [
        {
            "id": "1",
            "payload": {
                "content": "Python",
                "source": "user",
                "importance": 0.8,
                "created_at": "2026-07-27T00:00:00",
                "metadata": {},
            },
        }
    ]

    embedding_manager = Mock()
    embedding_manager.embed = AsyncMock(return_value=[0.1, 0.2])

    repository = QdrantRepository(
        vector_store=vector_store,
        embedding_manager=embedding_manager,
    )

    memories = await repository.search("Python")

    assert len(memories) == 1
    assert memories[0].content == "Python"

    vector_store.search.assert_called_once()
