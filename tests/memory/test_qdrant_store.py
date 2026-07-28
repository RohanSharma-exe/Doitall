from qdrant_client import QdrantClient

from doitall.memory.qdrant_store import QdrantStore


def test_qdrant_store_creation():
    client = QdrantClient(":memory:")

    store = QdrantStore(
        client=client,
        collection_name="test_collection",
    )

    assert store.client is client
    assert store.collection_name == "test_collection"
