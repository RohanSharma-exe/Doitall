from doitall.memory.store import MemoryStore
from doitall.models.memory import Memory


class MemoryManager:
    def __init__(
        self,
        store: MemoryStore,
    ) -> None:
        self._store = store

    def add(
        self,
        memory: Memory,
    ) -> None:
        self._store.add(memory)

    def all(
        self,
    ) -> list[Memory]:
        return self._store.get_all()

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        """
        Return memories relevant to the query.

        If the backing store supports semantic search, use it.
        Otherwise fall back to returning recent memories.
        """

        try:
            return self._store.search(
                query=query,
                limit=limit,
            )
        except NotImplementedError:
            return self._store.get_all()[-limit:]

    def clear(
        self,
    ) -> None:
        self._store.clear()

    def count(
        self,
    ) -> int:
        return self._store.count()
