"""Knowledge document Chunk payload serializer module."""

from typing import Any

from doitall.knowledge.chunk import Chunk


class ChunkSerializer:
    """Serializer converting Chunk models to/from vector store dictionary payloads."""

    @staticmethod
    def to_payload(
        chunk: Chunk,
    ) -> dict[str, Any]:
        """Convert Chunk model to vector payload dictionary."""
        return {
            "document_id": chunk.document_id,
            "text": chunk.text,
            "chunk_index": chunk.chunk_index,
            "metadata": chunk.metadata,
        }

    @staticmethod
    def from_payload(
        chunk_id: str,
        payload: dict[str, Any],
    ) -> Chunk:
        """Construct Chunk model from vector payload dictionary and chunk_id."""
        return Chunk(
            id=chunk_id,
            document_id=payload["document_id"],
            text=payload["text"],
            chunk_index=payload["chunk_index"],
            metadata=payload.get("metadata", {}),
        )
