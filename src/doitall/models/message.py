from enum import StrEnum

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1)


class SystemMessage(Message):
    role: MessageRole = MessageRole.SYSTEM


class UserMessage(Message):
    role: MessageRole = MessageRole.USER


class AssistantMessage(Message):
    role: MessageRole = MessageRole.ASSISTANT


class ToolMessage(Message):
    role: MessageRole = MessageRole.TOOL
