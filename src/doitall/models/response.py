"""High-level application response model."""

from pydantic import BaseModel, Field

from doitall.models.usage import Usage


class Response(BaseModel):
    """Unified application response object containing output content, model info, and token usage metrics."""

    content: str = Field(default="")
    model: str = Field(default="")
    provider: str = Field(default="")
    finish_reason: str | None = None
    usage: Usage = Field(default_factory=Usage)

