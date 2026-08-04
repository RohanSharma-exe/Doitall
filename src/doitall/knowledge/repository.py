"""Abstract knowledge repository interface module."""

from abc import ABC, abstractmethod

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
    def clear(self) -> None:
        """Delete indexed documents."""

    @abstractmethod
    def count(self) -> int:
        """Number of indexed chunks."""
