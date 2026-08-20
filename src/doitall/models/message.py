"""Chat message models for system, user, assistant, and tool roles."""

from enum import StrEnum

from pydantic import BaseModel, Field

from doitall.models.tool_call import ToolCall, ToolExecutionMetadata


class MessageRole(StrEnum):
    """Enumeration of standard chat completion message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """Base chat message representation."""

    role: MessageRole
    content: str = ""


class SystemMessage(Message):
    """System instruction prompt message."""

    role: MessageRole = MessageRole.SYSTEM


class UserMessage(Message):
    """User input prompt message."""

    role: MessageRole = MessageRole.USER


class AssistantMessage(Message):
    """Assistant output message, optionally containing tool call requests."""

    role: MessageRole = MessageRole.ASSISTANT

    tool_calls: list[ToolCall] = Field(
        default_factory=list,
    )


class ToolMessage(Message):
    """Tool execution response message associated with a tool call ID."""

    role: MessageRole = MessageRole.TOOL

    tool_call_id: str
    name: str
    execution_metadata: ToolExecutionMetadata | None = None
