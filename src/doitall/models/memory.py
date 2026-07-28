from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class Memory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))

    content: str

    source: str = "conversation"

    importance: float = 0.5

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    metadata: dict[str, str] = Field(default_factory=dict)
