"""Abstract document loader interface module."""

from abc import ABC, abstractmethod

from doitall.knowledge.document import Document


class DocumentLoader(ABC):
    """Abstract base class for document file loaders."""

    @abstractmethod
    def load(
        self,
        path: str,
    ) -> list[Document]:
        """Load one or more documents."""

