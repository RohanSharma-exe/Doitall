"""Qdrant vector repository implementation module."""

from doitall.embeddings.manager import EmbeddingManager
from doitall.memory.vector_repository import VectorRepository
from doitall.memory.vector_store import VectorStore
from doitall.models.memory import Memory
from doitall.serialization.memory_serializer import MemorySerializer


class QdrantRepository(VectorRepository):
    """Repository connecting Memory models to Qdrant vector store and embedding manager."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_manager: EmbeddingManager,
    ) -> None:
        """Initialize repository with vector store and embedding manager."""
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    async def save(
        self,
        memory: Memory,
    ) -> None:
        """Embed memory content and upsert point payload into Qdrant."""
        vector = await self.embedding_manager.embed(
            memory.content,
        )

        payload = MemorySerializer.to_payload(
            memory,
        )

        await self.vector_store.upsert(
            point_id=memory.id,
            vector=vector,
            payload=payload,
        )

    async def get_all(self, limit: int = 10000) -> list[Memory]:
        """Return all stored memories using scroll (no embedding needed)."""
        results = await self.vector_store.scroll_all(limit=limit)
        return [
            MemorySerializer.from_payload(
                memory_id=str(result["id"]),
                payload=result["payload"],
            )
            for result in results
        ]

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        """Embed search query string and return top-k matching Memory instances."""
        vector = await self.embedding_manager.embed(query)

        results = await self.vector_store.search(
            vector=vector,
            limit=limit,
        )

        return [
            MemorySerializer.from_payload(
                memory_id=str(result["id"]),
                payload=result["payload"],
            )
            for result in results
        ]

    async def delete(
        self,
        memory_id: str,
    ) -> None:
        """Delete memory point by ID from Qdrant."""
        await self.vector_store.delete(memory_id)

    async def clear(self) -> None:
        """Clear all stored memory points from Qdrant."""
        await self.vector_store.clear()

    async def count(self) -> int:
        """Return count of stored memory points in Qdrant."""
        return await self.vector_store.count()
