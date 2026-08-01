"""Structured streaming event models for chat responses."""

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

StreamEventType = Literal[
    "session",
    "metadata",
    "thinking",
    "token",
    "error",
    "done",
]


class StreamEvent(BaseModel):
    """A safe, public event emitted by the chat streaming endpoint."""

    event: StreamEventType
    data: dict[str, Any] = Field(default_factory=dict)
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ThinkingEvent(BaseModel):
    """A safe timeline update that never contains hidden reasoning or prompts."""

    label: str
    status: Literal["pending", "running", "completed", "failed"] = "running"
    detail: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
