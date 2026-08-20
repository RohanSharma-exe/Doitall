"""Abstract knowledge repository interface module."""

from abc import ABC, abstractmethod
from typing import Any

from doitall.knowledge.document import Document


class KnowledgeRepository(ABC):
    """Abstract base class defining the contract for RAG document knowledge repositories."""

    @abstractmethod
    async def add(
        self,
        document: Document,
    ) -> int:
        """Index a document and return the number of indexed chunks."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Document]:
        """Semantic search."""

    @abstractmethod
    async def delete(
        self,
        document_id: str,
    ) -> int:
        """Delete all chunks associated with *document_id*. Return the chunk count removed."""

    @abstractmethod
    async def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return a paged list of document summaries (id, title, chunk_count, metadata)."""

    @abstractmethod
    async def clear(self) -> None:
        """Delete all indexed documents."""

    @abstractmethod
    async def count(self) -> int:
        """Number of indexed chunks."""
