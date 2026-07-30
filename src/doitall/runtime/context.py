from typing import Any

from pydantic import BaseModel, Field

from doitall.knowledge.document import Document
from doitall.models.memory import Memory
from doitall.models.message import Message
from doitall.models.tool_definition import ToolDefinition


class RuntimeContext(BaseModel):
    """Context passed through the runtime execution pipeline.

    The RuntimeContext accumulates information from various context providers
    (conversation history, memories, knowledge, tools) and is used to build
    the final prompt sent to the LLM.
    """

    query: str = ""
    """The user's query or input."""

    messages: list[Message] = Field(default_factory=list)
    """Conversation history messages."""

    memories: list[Memory] = Field(default_factory=list)
    """Relevant memories retrieved from semantic search."""

    knowledge: list[Document] = Field(default_factory=list)
    """Relevant knowledge documents retrieved from RAG."""

    tools: list[ToolDefinition] = Field(default_factory=list)
    """Available tools/skills for the LLM to use."""

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )
    """Additional metadata for the context."""
