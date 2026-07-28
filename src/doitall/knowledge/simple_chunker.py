from doitall.knowledge.chunk import Chunk
from doitall.knowledge.chunker import DocumentChunker
from doitall.knowledge.document import Document


class SimpleChunker(DocumentChunker):
    def __init__(
        self,
        chunk_size: int = 500,
    ) -> None:
        self.chunk_size = chunk_size

    def chunk(
        self,
        document: Document,
    ) -> list[Chunk]:
        text = document.content

        return [
            Chunk(
                document_id=document.id,
                text=text[i : i + self.chunk_size],
                chunk_index=index,
            )
            for index, i in enumerate(range(0, len(text), self.chunk_size))
        ]
