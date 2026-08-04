"""In-memory implementation of MemoryStore interface."""

from doitall.memory.store import MemoryStore
from doitall.models.memory import Memory


class InMemoryStore(MemoryStore):
    """In-memory list backed memory store for tests and fast transient execution."""

    def __init__(self) -> None:
        """Initialize empty memory list."""
        self._memories: list[Memory] = []

    async def add(self, memory: Memory) -> None:
        """Append memory record to internal list."""
        self._memories.append(memory)

    async def get_all(self) -> list[Memory]:
        """Return shallow copy of stored memories list."""
        return self._memories.copy()

    async def clear(self) -> None:
        """Clear all stored memories from memory list."""
        self._memories.clear()

    async def count(self) -> int:
        """Return number of stored memory objects."""
        return len(self._memories)

