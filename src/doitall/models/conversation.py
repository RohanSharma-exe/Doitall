from pydantic import BaseModel, Field

from doitall.models.message import Message


class Conversation(BaseModel):
    messages: list[Message] = Field(default_factory=list)

    def add(self, message: Message) -> None:
        self.messages.append(message)

    def clear(self) -> None:
        self.messages.clear()

    def last(self) -> Message | None:
        if not self.messages:
            return None

        return self.messages[-1]
