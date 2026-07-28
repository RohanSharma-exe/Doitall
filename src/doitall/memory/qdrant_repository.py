from doitall.embeddings.manager import EmbeddingManager
from doitall.memory.vector_repository import VectorRepository
from doitall.memory.vector_store import VectorStore
from doitall.models.memory import Memory
from doitall.serialization.memory_serializer import MemorySerializer


class QdrantRepository(VectorRepository):
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_manager: EmbeddingManager,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def save(
        self,
        memory: Memory,
    ) -> None:
        vector = self.embedding_manager.embed(
            memory.content,
        )

        payload = MemorySerializer.to_payload(
            memory,
        )

        self.vector_store.upsert(
            point_id=memory.id,
            vector=vector,
            payload=payload,
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        vector = self.embedding_manager.embed(query)

        results = self.vector_store.search(
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

    def delete(
        self,
        memory_id: str,
    ) -> None:
        self.vector_store.delete(memory_id)

    def clear(self) -> None:
        self.vector_store.clear()

    def count(self) -> int:
        return self.vector_store.count()
