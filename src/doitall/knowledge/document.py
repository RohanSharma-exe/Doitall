"""Knowledge base document model."""

from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Knowledge document containing raw text content, source path, and metadata."""

    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex)

    content: str

    source: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

