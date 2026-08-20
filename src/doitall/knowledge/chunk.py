"""Knowledge document chunk data model."""

import hashlib
import uuid
from typing import Any, Self

from pydantic import BaseModel, Field, model_validator


class Chunk(BaseModel):
    """Sub-segment chunk extracted from a parent document for indexing."""

    id: str = ""

    document_id: str

    text: str

    chunk_index: int

    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def set_deterministic_id(self) -> Self:
        """Derive a stable, UUID-compatible ID when callers do not provide one."""
        if self.id:
            return self

        content_hash = hashlib.sha256(self.text.encode("utf-8")).hexdigest()
        identity = f"{self.document_id}:{self.chunk_index}:{content_hash}"
        self.id = uuid.uuid5(uuid.NAMESPACE_URL, identity).hex
        return self
