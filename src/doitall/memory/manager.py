from doitall.core.exceptions import ProviderError, ValidationError
from doitall.memory.store import MemoryStore
from doitall.models.memory import Memory


class MemoryManager:
    def __init__(
        self,
        store: MemoryStore,
    ) -> None:
        self._store = store

    async def add(
        self,
        memory: Memory,
    ) -> None:
        if not memory or not memory.content or not memory.content.strip():
            raise ValidationError("Memory content cannot be empty")

        await self._store.add(memory)

    async def all(
        self,
    ) -> list[Memory]:
        try:
            return await self._store.get_all()
        except Exception as e:
            raise ProviderError(f"Failed to retrieve all memories: {e}") from e

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        """
        Return memories relevant to the query.

        If the backing store supports semantic search, use it.
        Otherwise fall back to returning recent memories.
        """

        if not query or not query.strip():
            return []

        try:
            return await self._store.search(
                query=query,
                limit=limit,
            )
        except NotImplementedError:
            memories = await self._store.get_all()
            return memories[-limit:]
        except Exception as e:
            raise ProviderError(f"Failed to search memories: {e}") from e

    async def clear(
        self,
    ) -> None:
        try:
            await self._store.clear()
        except Exception as e:
            raise ProviderError(f"Failed to clear memories: {e}") from e

    async def count(
        self,
    ) -> int:
        try:
            return await self._store.count()
        except Exception as e:
            raise ProviderError(f"Failed to count memories: {e}") from e
