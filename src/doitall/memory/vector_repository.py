from abc import ABC, abstractmethod

from doitall.models.memory import Memory


class VectorRepository(ABC):
    @abstractmethod
    def save(self, memory: Memory) -> None:
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        pass

    @abstractmethod
    def delete(
        self,
        memory_id: str,
    ) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
