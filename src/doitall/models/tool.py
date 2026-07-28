from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str = ""
    required: bool = True


class Tool(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)
