from doitall.memory.store import MemoryStore
from doitall.models.memory import Memory


class InMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._memories: list[Memory] = []

    async def add(self, memory: Memory) -> None:
        self._memories.append(memory)

    async def get_all(self) -> list[Memory]:
        return self._memories.copy()

    def clear(self) -> None:
        self._memories.clear()

    def count(self) -> int:
        return len(self._memories)
