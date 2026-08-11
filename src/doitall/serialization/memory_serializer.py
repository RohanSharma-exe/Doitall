"""Memory model vector payload serializer module."""

from datetime import datetime
from typing import Any

from doitall.models.memory import Memory


class MemorySerializer:
    """Serializer converting Memory domain models to/from vector payload dictionaries."""

    @staticmethod
    def to_payload(
        memory: Memory,
    ) -> dict[str, Any]:
        """Serialize Memory object into Qdrant-compatible JSON payload dict."""
        return {
            "content": memory.content,
            "source": memory.source,
            "importance": memory.importance,
            "created_at": memory.created_at.isoformat(),
            "metadata": memory.metadata,
        }

    @staticmethod
    def from_payload(
        memory_id: str,
        payload: dict[str, Any],
    ) -> Memory:
        """Construct Memory object from vector point payload dict and memory_id."""
        return Memory(
            id=memory_id,
            content=payload["content"],
            source=payload.get("source", "conversation"),
            importance=payload.get("importance", 0.5),
            created_at=datetime.fromisoformat(payload["created_at"]),
            metadata=payload.get("metadata", {}),
        )
