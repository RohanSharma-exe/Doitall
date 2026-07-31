from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from doitall.config.settings import settings
from doitall.memory.constants import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_DISTANCE,
    get_vector_size_for_model,
)
from doitall.memory.vector_store import VectorStore


class QdrantStore(VectorStore):
    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        vector_size: int | None = None,
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size or get_vector_size_for_model(
            settings.EMBEDDING_MODEL
        )

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections

        if any(collection.name == self.collection_name for collection in collections):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance[DEFAULT_DISTANCE],
            ),
        )

    def upsert(
        self,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        self.client.upsert(
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

    def search(
        self,
        vector: list[float],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points

        return [
            {
                "id": str(point.id),
                "score": point.score,
                "payload": point.payload,
            }
            for point in results
        ]

    def scroll_all(
        self,
        limit: int = 10000,
    ) -> list[dict[str, Any]]:
        """Return all stored points using Qdrant scroll (no embedding needed)."""
        points, _next = self.client.scroll(
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

    def delete(
        self,
        point_id: str,
    ) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[point_id],
        )

    def count(self) -> int:
        info = self.client.get_collection(
            self.collection_name,
        )

        return info.points_count or 0

    def clear(self) -> None:
        self.client.delete_collection(
            self.collection_name,
        )

        self._ensure_collection()

