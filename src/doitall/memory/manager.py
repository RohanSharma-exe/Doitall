from doitall.memory.store import MemoryStore
from doitall.models.memory import Memory


class MemoryManager:
    def __init__(self, store: MemoryStore):
        self.store = store

    def add(self, memory: Memory) -> None:
        self.store.add(memory)

    def all(self) -> list[Memory]:
        return self.store.get_all()

    def clear(self) -> None:
        self.store.clear()

    def count(self) -> int:
        return self.store.count()
