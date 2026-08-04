"""Message domain model dictionary serializer module."""

from typing import Any

from doitall.models.message import Message


class MessageSerializer:
    """Serializer converting Message domain models to/from plain Python dictionaries."""

    @staticmethod
    def to_dict(
        message: Message,
    ) -> dict[str, Any]:
        """Convert Message object into raw dictionary."""
        return {
            "role": message.role.value,
            "content": message.content,
            "name": message.name,
            "tool_call_id": message.tool_call_id,
            "metadata": message.metadata,
        }

    @staticmethod
    def from_dict(
        data: dict[str, Any],
    ) -> Message:
        """Validate and construct Message object from raw dictionary data."""
        return Message.model_validate(data)

