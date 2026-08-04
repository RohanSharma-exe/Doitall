"""AI Agent configuration data model."""

from pydantic import BaseModel, Field


class Agent(BaseModel):
    """Specification of an AI agent assistant with system prompts and assigned tools."""

    name: str

    description: str = ""

    system_prompt: str = ""

    tools: list[str] = Field(default_factory=list)

    metadata: dict[str, str] = Field(default_factory=dict)
