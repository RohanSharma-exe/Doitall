"""Abstract document parser interface module."""

from abc import ABC, abstractmethod

from doitall.knowledge.document import Document


class DocumentParser(ABC):
    """Abstract base class for document file parsers."""

    @abstractmethod
    def parse(
        self,
        path: str,
    ) -> list[Document]:
        """Parse a file into one or more documents."""
