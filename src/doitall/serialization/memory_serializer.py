from datetime import datetime
from typing import Any

from doitall.models.memory import Memory


class MemorySerializer:
    @staticmethod
    def to_payload(
        memory: Memory,
    ) -> dict[str, Any]:
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
        return Memory(
            id=memory_id,
            content=payload["content"],
            source=payload.get("source"),
            importance=payload.get("importance", 0.5),
            created_at=datetime.fromisoformat(payload["created_at"]),
            metadata=payload.get("metadata", {}),
        )
