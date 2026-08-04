"""VectorRepository adapter for MemoryStore interface."""

from doitall.memory.store import MemoryStore
from doitall.memory.vector_repository import VectorRepository
from doitall.models.memory import Memory


class VectorMemoryStore(MemoryStore):
    """MemoryStore implementation wrapping a VectorRepository backend."""

    def __init__(
        self,
        repository: VectorRepository,
    ) -> None:
        """Initialize VectorMemoryStore with backing VectorRepository instance."""
        self.repository = repository

    async def add(
        self,
        memory: Memory,
    ) -> None:
        """Save Memory instance into backing repository."""
        await self.repository.save(memory)

    async def get_all(self) -> list[Memory]:
        """Return all memories using scroll — no embedding call needed."""
        return await self.repository.get_all()

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        """Perform semantic search for matching memories in repository."""
        return await self.repository.search(
            query=query,
            limit=limit,
        )

    async def delete(
        self,
        memory_id: str,
    ) -> None:
        """Delete memory by memory_id in backing repository."""
        await self.repository.delete(memory_id)

    async def clear(self) -> None:
        """Clear all memories in backing repository."""
        await self.repository.clear()

    async def count(self) -> int:
        """Return count of stored memories in repository."""
        return await self.repository.count()

