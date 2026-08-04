"""Conversation history data container."""

from pydantic import BaseModel, Field

from doitall.models.message import Message


class Conversation(BaseModel):
    """Container managing ordered chat history messages."""

    messages: list[Message] = Field(default_factory=list)

    def add(self, message: Message) -> None:
        """Append a new message to the conversation history."""
        self.messages.append(message)

    def clear(self) -> None:
        """Clear all messages from the conversation history."""
        self.messages.clear()

    def last(self) -> Message | None:
        """Return the most recent message in the conversation, or None if empty."""
        if not self.messages:
            return None

        return self.messages[-1]
