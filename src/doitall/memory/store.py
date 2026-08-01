from abc import ABC, abstractmethod

from doitall.models.memory import Memory


class MemoryStore(ABC):
    @abstractmethod
    async def add(
        self,
        memory: Memory,
    ) -> None:
        pass

    @abstractmethod
    async def get_all(self) -> list[Memory]:
        pass

    @abstractmethod
    async def clear(self) -> None:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        raise NotImplementedError

    async def delete(
        self,
        memory_id: str,
    ) -> None:
        raise NotImplementedError
