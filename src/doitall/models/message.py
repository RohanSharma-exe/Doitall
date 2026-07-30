from enum import StrEnum

from pydantic import BaseModel, Field

from doitall.models.tool_call import ToolCall


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: MessageRole
    content: str = ""


class SystemMessage(Message):
    role: MessageRole = MessageRole.SYSTEM


class UserMessage(Message):
    role: MessageRole = MessageRole.USER


class AssistantMessage(Message):
    role: MessageRole = MessageRole.ASSISTANT

    tool_calls: list[ToolCall] = Field(
        default_factory=list,
    )


class ToolMessage(Message):
    role: MessageRole = MessageRole.TOOL

    tool_call_id: str
    name: str
