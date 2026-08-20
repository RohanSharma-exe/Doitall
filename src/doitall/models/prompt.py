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

    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, gt=0)
