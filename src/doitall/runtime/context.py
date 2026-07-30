from typing import Any

from pydantic import BaseModel, Field

from doitall.knowledge.document import Document
from doitall.models.memory import Memory
from doitall.models.message import Message
from doitall.models.tool_definition import ToolDefinition


class RuntimeContext(BaseModel):
    query: str = ""

    messages: list[Message] = Field(default_factory=list)

    memories: list[Memory] = Field(default_factory=list)

    knowledge: list[Document] = Field(default_factory=list)

    tools: list[ToolDefinition] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )
