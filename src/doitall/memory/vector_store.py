from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):
    """Async abstract interface for vector storage backends."""

    @abstractmethod
    async def upsert(
        self,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        pass

    async def upsert_many(
        self,
        points: list[tuple[str, list[float], dict[str, Any]]],
    ) -> None:
        """Upsert multiple points, with a sequential fallback for simple stores."""
        for point_id, vector, payload in points:
            await self.upsert(point_id=point_id, vector=vector, payload=payload)

    @abstractmethod
    async def search(
        self,
        vector: list[float],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def scroll_all(
        self,
        limit: int = 10000,
    ) -> list[dict[str, Any]]:
        """Return all records without performing a vector search.

        Unlike ``search()``, this method does **not** require an embedding
        vector, making it safe to call when you simply want every stored
        record (e.g. ``get_all`` on the memory store).
        """

    @abstractmethod
    async def get_by_document_id(
        self,
        document_id: str,
    ) -> list[dict[str, Any]]:
        """Return all stored points whose payload ``document_id`` equals *document_id*.

        Implementations must perform a filtered lookup rather than scanning the
        entire collection.  The return format matches ``scroll_all``:
        ``[{"id": str, "payload": dict}, ...]``.
        """

    @abstractmethod
    async def delete(
        self,
        point_id: str,
    ) -> None:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def clear(self) -> None:
        pass
