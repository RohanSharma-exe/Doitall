from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):
    @abstractmethod
    def upsert(
        self,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        pass

    @abstractmethod
    def search(
        self,
        vector: list[float],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def scroll_all(
        self,
        limit: int = 10000,
    ) -> list[dict[str, Any]]:
        """Return all records without performing a vector search.

        Unlike ``search()``, this method does **not** require an embedding
        vector, making it safe to call when you simply want every stored
        record (e.g. ``get_all`` on the memory store).
        """

    @abstractmethod
    def delete(
        self,
        point_id: str,
    ) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
