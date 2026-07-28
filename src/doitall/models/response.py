from pydantic import BaseModel, Field

from doitall.models.usage import Usage


class Response(BaseModel):
    content: str = Field(default="")
    model: str = Field(default="")
    provider: str = Field(default="")
    finish_reason: str | None = None
    usage: Usage = Field(default_factory=Usage)
