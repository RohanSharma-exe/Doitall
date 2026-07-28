from pydantic import BaseModel, Field


class Agent(BaseModel):
    name: str

    description: str = ""

    system_prompt: str = ""

    tools: list[str] = Field(default_factory=list)

    metadata: dict[str, str] = Field(default_factory=dict)
