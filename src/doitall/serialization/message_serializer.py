"""Message domain model dictionary serializer module."""

from typing import Any

from doitall.models.message import Message


class MessageSerializer:
    """Serializer converting Message domain models to/from plain Python dictionaries."""

    @staticmethod
    def to_dict(
        message: Message,
    ) -> dict[str, Any]:
        """Convert Message object into raw dictionary.

        Handles all message subtypes (System, User, Assistant, Tool)
        gracefully by only including fields that exist on the concrete
        instance.
        """
        data: dict[str, Any] = {
            "role": message.role.value,
            "content": message.content,
        }

        # ToolMessage fields
        name = getattr(message, "name", None)
        if name is not None:
            data["name"] = name

        tool_call_id = getattr(message, "tool_call_id", None)
        if tool_call_id is not None:
            data["tool_call_id"] = tool_call_id

        # AssistantMessage tool_calls
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            data["tool_calls"] = [tc.model_dump() for tc in tool_calls]

        return data

    @staticmethod
    def from_dict(
        data: dict[str, Any],
    ) -> Message:
        """Validate and construct Message object from raw dictionary data."""
        return Message.model_validate(data)
