from unittest.mock import AsyncMock, MagicMock

import pytest
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from doitall.memory.qdrant_store import QdrantStore


def test_qdrant_store_creation():
    client = AsyncQdrantClient(":memory:")

    store = QdrantStore(
        client=client,
        collection_name="test_collection",
    )

    assert store.client is client
    assert store.collection_name == "test_collection"


@pytest.mark.asyncio
async def test_get_by_document_id_filters_by_payload():
    """get_by_document_id must call client.scroll with a document_id payload filter.

    The Qdrant client is mocked so no live server is required.
    """
    # Build two fake point objects that the mocked scroll will return.
    def _make_point(point_id: str, doc_id: str) -> MagicMock:
        pt = MagicMock()
        pt.id = point_id
        pt.payload = {"document_id": doc_id, "text": "hello", "metadata": {}}
        return pt

    fake_points = [
        _make_point("chunk-1", "doc-test"),
        _make_point("chunk-2", "doc-test"),
    ]

    mock_client = MagicMock(spec=AsyncQdrantClient)
    # client.scroll returns (points, next_page_offset)
    mock_client.scroll = AsyncMock(return_value=(fake_points, None))

    store = QdrantStore(
        client=mock_client,
        collection_name="knowledge",
        vector_size=384,
    )

    results = await store.get_by_document_id("doc-test")

    # Verify client.scroll was called exactly once.
    mock_client.scroll.assert_awaited_once()

    call_kwargs = mock_client.scroll.await_args.kwargs

    # Verify the filter targets the correct payload field and value.
    scroll_filter: Filter = call_kwargs["scroll_filter"]
    assert isinstance(scroll_filter, Filter)
    assert scroll_filter.must is not None
    assert len(scroll_filter.must) == 1

    condition: FieldCondition = scroll_filter.must[0]
    assert isinstance(condition, FieldCondition)
    assert condition.key == "document_id"
    assert isinstance(condition.match, MatchValue)
    assert condition.match.value == "doc-test"

    # Verify the expected results are returned.
    assert len(results) == 2
    assert results[0]["id"] == "chunk-1"
    assert results[1]["id"] == "chunk-2"
    assert results[0]["payload"]["document_id"] == "doc-test"
