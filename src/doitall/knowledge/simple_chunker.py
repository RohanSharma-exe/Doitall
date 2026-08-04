"""Fixed-length character chunker module."""

from doitall.knowledge.chunk import Chunk
from doitall.knowledge.chunker import DocumentChunker
from doitall.knowledge.document import Document


class SimpleChunker(DocumentChunker):
    """Splits Document text into fixed-size character slice chunks."""

    def __init__(
        self,
        chunk_size: int = 500,
    ) -> None:
        """Initialize chunker with character chunk_size limit (default 500 chars)."""
        self.chunk_size = chunk_size

    def chunk(
        self,
        document: Document,
    ) -> list[Chunk]:
        """Split document content into list of Chunk objects."""
        text = document.content

        return [
            Chunk(
                document_id=document.id,
                text=text[i : i + self.chunk_size],
                chunk_index=index,
            )
            for index, i in enumerate(range(0, len(text), self.chunk_size))
        ]
