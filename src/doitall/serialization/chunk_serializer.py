from typing import Any

from doitall.knowledge.chunk import Chunk


class ChunkSerializer:
    @staticmethod
    def to_payload(
        chunk: Chunk,
    ) -> dict[str, Any]:
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
        return Chunk(
            id=chunk_id,
            document_id=payload["document_id"],
            text=payload["text"],
            chunk_index=payload["chunk_index"],
            metadata=payload.get("metadata", {}),
        )
