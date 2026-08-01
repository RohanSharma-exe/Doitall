from unittest.mock import AsyncMock, Mock

import pytest

from doitall.knowledge.document import Document
from doitall.knowledge.simple_chunker import SimpleChunker
from doitall.knowledge.vector_repository import VectorKnowledgeRepository
from doitall.serialization.chunk_serializer import ChunkSerializer


def _make_async_vector_store() -> Mock:
    """Return a Mock whose async VectorStore methods are all AsyncMock."""
    store = Mock()
    store.upsert = AsyncMock()
    store.search = AsyncMock(return_value=[])
    store.scroll_all = AsyncMock(return_value=[])
    store.delete = AsyncMock()
    store.count = AsyncMock(return_value=0)
    store.clear = AsyncMock()
    return store


@pytest.mark.asyncio
async def test_add_document():
    chunker = Mock()
    embedding_manager = Mock()
    vector_store = _make_async_vector_store()

    chunk = Mock()
    chunk.id = "chunk-1"
    chunk.document_id = "doc-1"
    chunk.text = "hello"
    chunk.chunk_index = 0
    chunk.metadata = {}

    chunker.chunk.return_value = [chunk]
    embedding_manager.embed = AsyncMock(return_value=[0.1, 0.2])

    repository = VectorKnowledgeRepository(
        chunker=chunker,
        embedding_manager=embedding_manager,
        vector_store=vector_store,
    )

    chunk_count = await repository.add(Document(id="doc-1", content="hello"))

    vector_store.upsert.assert_called_once_with(
        point_id="chunk-1",
        vector=[0.1, 0.2],
        payload=ChunkSerializer.to_payload(chunk),
    )
    assert chunk_count == 1


def test_repository_creation():
    repository = VectorKnowledgeRepository(
        chunker=SimpleChunker(),
        embedding_manager=Mock(),
        vector_store=_make_async_vector_store(),
    )

    assert repository is not None


@pytest.mark.asyncio
async def test_repository_count():
    vector_store = _make_async_vector_store()
    vector_store.count = AsyncMock(return_value=10)

    repository = VectorKnowledgeRepository(
        chunker=Mock(),
        embedding_manager=Mock(),
        vector_store=vector_store,
    )

    assert await repository.count() == 10
    vector_store.count.assert_called_once()


@pytest.mark.asyncio
async def test_count():
    vector_store = _make_async_vector_store()
    vector_store.count = AsyncMock(return_value=42)

    repository = VectorKnowledgeRepository(
        chunker=SimpleChunker(),
        embedding_manager=Mock(),
        vector_store=vector_store,
    )

    assert await repository.count() == 42


@pytest.mark.asyncio
async def test_clear():
    vector_store = _make_async_vector_store()

    repository = VectorKnowledgeRepository(
        chunker=SimpleChunker(),
        embedding_manager=Mock(),
        vector_store=vector_store,
    )

    await repository.clear()

    vector_store.clear.assert_called_once()


@pytest.mark.asyncio
async def test_search():
    chunker = Mock()
    embedding_manager = Mock()
    vector_store = _make_async_vector_store()

    embedding_manager.embed = AsyncMock(return_value=[1.0])

    vector_store.search = AsyncMock(
        return_value=[
            {
                "payload": {
                    "document_id": "doc1",
                    "text": "Hello World",
                    "metadata": {},
                }
            }
        ]
    )

    repository = VectorKnowledgeRepository(
        chunker=chunker,
        embedding_manager=embedding_manager,
        vector_store=vector_store,
    )

    results = await repository.search("hello")

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].content == "Hello World"


@pytest.mark.asyncio
async def test_add_multiple_chunks():
    chunker = Mock()
    embedding_manager = Mock()
    vector_store = _make_async_vector_store()

    chunk1 = Mock()
    chunk1.id = "1"
    chunk1.document_id = "doc"
    chunk1.text = "first"
    chunk1.chunk_index = 0
    chunk1.metadata = {}

    chunk2 = Mock()
    chunk2.id = "2"
    chunk2.document_id = "doc"
    chunk2.text = "second"
    chunk2.chunk_index = 1
    chunk2.metadata = {}

    chunker.chunk.return_value = [chunk1, chunk2]
    embedding_manager.embed = AsyncMock(side_effect=[[0.1], [0.2]])

    repository = VectorKnowledgeRepository(
        chunker=chunker,
        embedding_manager=embedding_manager,
        vector_store=vector_store,
    )

    await repository.add(Document(content="hello"))

    assert vector_store.upsert.call_count == 2


@pytest.mark.asyncio
async def test_search_returns_empty():
    embedding_manager = Mock()
    vector_store = _make_async_vector_store()

    embedding_manager.embed = AsyncMock(return_value=[1.0])
    vector_store.search = AsyncMock(return_value=[])

    repository = VectorKnowledgeRepository(
        chunker=Mock(),
        embedding_manager=embedding_manager,
        vector_store=vector_store,
    )

    result = await repository.search("hello")
    assert result == []
