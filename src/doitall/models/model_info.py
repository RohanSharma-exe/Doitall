"""LLM model capability metadata model."""

from pydantic import BaseModel


class ModelInfo(BaseModel):
    """Metadata describing capabilities, context window, and limits of an LLM model."""

    provider: str
    id: str
    name: str

    context_window: int | None = None
    max_output_tokens: int | None = None

    supports_chat: bool = True
    supports_streaming: bool = False
    supports_embeddings: bool = False
    supports_vision: bool = False
    supports_image_generation: bool = False
    supports_audio: bool = False
    supports_tool_calling: bool = False
