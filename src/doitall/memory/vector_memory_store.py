from doitall.memory.store import MemoryStore
from doitall.memory.vector_repository import VectorRepository
from doitall.models.memory import Memory


class VectorMemoryStore(MemoryStore):
    def __init__(
        self,
        repository: VectorRepository,
    ) -> None:
        self.repository = repository

    async def add(
        self,
        memory: Memory,
    ) -> None:
        await self.repository.save(memory)

    async def get_all(self) -> list[Memory]:
        """Return all memories using scroll — no embedding call needed."""
        return await self.repository.get_all()

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        return await self.repository.search(
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

