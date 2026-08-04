"""Knowledge document chunk data model."""

from typing import Any

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """Sub-segment chunk extracted from a parent document for indexing."""

    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex)

    document_id: str

    text: str

    chunk_index: int

    metadata: dict[str, Any] = Field(default_factory=dict)

