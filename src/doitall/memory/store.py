from abc import ABC, abstractmethod

from doitall.models.memory import Memory


class MemoryStore(ABC):
    @abstractmethod
    def add(
        self,
        memory: Memory,
    ) -> None:
        pass

    @abstractmethod
    def get_all(self) -> list[Memory]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        raise NotImplementedError

    def delete(
        self,
        memory_id: str,
    ) -> None:
        raise NotImplementedError
