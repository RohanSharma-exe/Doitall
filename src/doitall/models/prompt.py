"""LLM request prompt specification model."""

from pydantic import BaseModel, Field

from doitall.models.attachment import Attachment
from doitall.models.tool import Tool


class Prompt(BaseModel):
    """Specification of an incoming execution prompt with tools, attachments, and parameters."""

    system_prompt: str | None = None
    user_prompt: str

    attachments: list[Attachment] = Field(default_factory=list)
    tools: list[Tool] = Field(default_factory=list)

    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int | None = None
