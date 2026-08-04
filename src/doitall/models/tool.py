"""Tool and parameter representation models."""

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Specification of an individual parameter for a tool."""

    name: str
    type: str
    description: str = ""
    required: bool = True


class Tool(BaseModel):
    """Declarative specification of a tool exposed to an LLM."""

    name: str
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)

