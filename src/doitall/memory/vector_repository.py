"""Abstract VectorRepository interface module."""

from abc import ABC, abstractmethod

from doitall.models.memory import Memory


class VectorRepository(ABC):
    """Abstract base class defining contract for vector-backed memory repositories."""

    @abstractmethod
    async def save(self, memory: Memory) -> None:
        """Save Memory instance."""

    @abstractmethod
    async def get_all(self, limit: int = 10000) -> list[Memory]:
        """Return all stored memories without requiring an embedding vector."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        """Search memories using query string."""

    @abstractmethod
    async def delete(
        self,
        memory_id: str,
    ) -> None:
        """Delete memory point by memory_id."""

    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored memory points."""

    @abstractmethod
    async def count(self) -> int:
        """Return total count of stored memory points."""

