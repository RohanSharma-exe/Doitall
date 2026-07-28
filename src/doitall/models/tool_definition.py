from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Metadata describing a callable tool."""

    name: str
    description: str

    input_schema: dict[str, Any] = Field(
        default_factory=dict,
    )
