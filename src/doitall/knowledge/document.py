from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex)

    content: str

    source: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)
