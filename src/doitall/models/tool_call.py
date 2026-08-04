"""Tool execution invocation and result models."""

from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """A tool invocation requested by an LLM."""

    id: str | None = None

    name: str

    arguments: dict[str, Any] = Field(
        default_factory=dict,
    )


class ToolResult(BaseModel):
    """Result returned from executing a tool."""

    tool_call_id: str | None = None

    name: str

    result: Any

