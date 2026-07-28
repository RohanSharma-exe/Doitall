from doitall.memory.store import MemoryStore
from doitall.memory.vector_repository import VectorRepository
from doitall.models.memory import Memory


class VectorMemoryStore(MemoryStore):
    def __init__(
        self,
        repository: VectorRepository,
    ) -> None:
        self.repository = repository

    def add(
        self,
        memory: Memory,
    ) -> None:
        self.repository.save(memory)

    def get_all(self) -> list[Memory]:
        return self.repository.search(
            query="",
            limit=10000,
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        return self.repository.search(
            query=query,
            limit=limit,
        )

    def delete(
        self,
        memory_id: str,
    ) -> None:
        self.repository.delete(memory_id)

    def clear(self) -> None:
        self.repository.clear()

    def count(self) -> int:
        return self.repository.count()
