"""Abstract document chunker interface module."""

from abc import ABC, abstractmethod

from doitall.knowledge.chunk import Chunk
from doitall.knowledge.document import Document


class DocumentChunker(ABC):
    """Abstract base class defining document chunking logic."""

    @abstractmethod
    def chunk(
        self,
        document: Document,
    ) -> list[Chunk]:
        """Split a document into chunks."""

