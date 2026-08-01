from pydantic import BaseModel, Field

from doitall.models.tool_call import ToolCall


class ProviderResponse(BaseModel):
    """Normalized response returned by an LLM provider."""

    content: str = ""

    tool_calls: list[ToolCall] = Field(
        default_factory=list,
    )

    finish_reason: str | None = None

    model: str | None = None

    usage_tokens: dict[str, int] = Field(default_factory=dict)
