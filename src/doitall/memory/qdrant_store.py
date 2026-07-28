from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from doitall.memory.constants import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_DISTANCE,
    DEFAULT_VECTOR_SIZE,
)
from doitall.memory.vector_store import VectorStore


class QdrantStore(VectorStore):
    def __init__(
        self,
        client: QdrantClient,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        self.client = client
        self.collection_name = collection_name

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections

        if any(collection.name == self.collection_name for collection in collections):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=DEFAULT_VECTOR_SIZE,
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
