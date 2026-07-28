from typing import Any

from doitall.models.message import Message


class MessageSerializer:
    @staticmethod
    def to_dict(
        message: Message,
    ) -> dict[str, Any]:
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
        return Message.model_validate(data)
