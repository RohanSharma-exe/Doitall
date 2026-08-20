from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from doitall.config.settings import settings
from doitall.memory.constants import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_DISTANCE,
    get_vector_size_for_model,
)
from doitall.memory.vector_store import VectorStore


class QdrantStore(VectorStore):
    """Async Qdrant-backed vector store.

    Uses ``AsyncQdrantClient`` so every network call yields control back
    to the event loop instead of blocking the thread.
    """

    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        vector_size: int | None = None,
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size or get_vector_size_for_model(
            settings.EMBEDDING_MODEL
        )
        # NOTE: collection creation is deferred to an explicit async
        # ``ensure_collection()`` call during bootstrap because __init__
        # cannot be async.

    async def ensure_collection(self) -> None:
        """Create the Qdrant collection if it does not already exist."""
        collections = (await self.client.get_collections()).collections

        if any(collection.name == self.collection_name for collection in collections):
            return

        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance[DEFAULT_DISTANCE],
            ),
        )

    async def upsert(
        self,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Upsert vector point with associated metadata payload."""
        await self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    async def upsert_many(
        self,
        points: list[tuple[str, list[float], dict[str, Any]]],
    ) -> None:
        """Submit a complete point batch in one Qdrant update request."""
        if not points:
            return
        await self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=[
                PointStruct(id=point_id, vector=vector, payload=payload)
                for point_id, vector, payload in points
            ],
        )

    async def search(
        self,
        vector: list[float],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Search vector space for top-k closest points to target query vector."""
        results = (
            await self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit,
                with_payload=True,
            )
        ).points

        return [
            {
                "id": str(point.id),
                "score": point.score,
                "payload": point.payload,
            }
            for point in results
        ]

    async def scroll_all(
        self,
        limit: int = 10000,
    ) -> list[dict[str, Any]]:
        """Return all stored points using Qdrant scroll (no embedding needed)."""
        points, _next = await self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [
            {
                "id": str(point.id),
                "payload": point.payload,
            }
            for point in points
        ]

    async def delete(
        self,
        point_id: str,
    ) -> None:
        """Delete point by point_id from Qdrant collection."""
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=[point_id],
        )

    async def count(self) -> int:
        """Return point_count of the collection."""
        info = await self.client.get_collection(
            self.collection_name,
        )
        return info.points_count or 0

    async def clear(self) -> None:
        """Drop collection and recreate empty collection."""
        await self.client.delete_collection(
            self.collection_name,
        )
        await self.ensure_collection()
