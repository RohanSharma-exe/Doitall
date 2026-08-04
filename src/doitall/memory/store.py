"""Abstract MemoryStore interface module."""

from abc import ABC, abstractmethod

from doitall.models.memory import Memory


class MemoryStore(ABC):
    """Abstract base class defining contract for long-term memory storage implementations."""

    @abstractmethod
    async def add(
        self,
        memory: Memory,
    ) -> None:
        """Add a new memory record."""

    @abstractmethod
    async def get_all(self) -> list[Memory]:
        """Return all stored memories."""

    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored memories."""

    @abstractmethod
    async def count(self) -> int:
        """Return total count of stored memories."""

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        """Search memories using query string (optional override)."""
        raise NotImplementedError

    async def delete(
        self,
        memory_id: str,
    ) -> None:
        """Delete specific memory by memory_id (optional override)."""
        raise NotImplementedError
