"""
REST API request and response models for the Doitall framework.
"""

import json
import math
from typing import Any

from pydantic import BaseModel, Field, field_validator

from doitall.config.settings import settings

# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Request body for a chat turn."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=settings.CHAT_MESSAGE_MAX_LENGTH,
        description="The user's message.",
    )
    provider: str | None = Field(
        default=None,
        description="Override the default provider (e.g. 'openai', 'groq').",
    )
    model: str | None = Field(
        default=None,
        description="Override the provider's configured default model.",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional session identifier for tracking.",
    )


class ChatResponse(BaseModel):
    """Response body from a chat turn.

    Includes a ChatGPT/Claude-style assistant message object while keeping
    the legacy ``response`` string for existing clients.
    """

    response: str
    message: dict[str, str] = Field(default_factory=dict)
    model: str | None = None
    usage_tokens: dict[str, int] = Field(default_factory=dict)
    session_id: str | None = None


# ---------------------------------------------------------------------------
# Knowledge ingestion
# ---------------------------------------------------------------------------

MAX_METADATA_KEYS = 100
MAX_METADATA_SERIALIZED_BYTES = 16 * 1024
MAX_METADATA_DEPTH = 5
MAX_METADATA_KEY_LENGTH = 128


def _validate_metadata_value(value: Any, *, depth: int) -> None:
    if depth > MAX_METADATA_DEPTH:
        raise ValueError(f"metadata nesting depth may not exceed {MAX_METADATA_DEPTH}")

    if isinstance(value, dict):
        if len(value) > MAX_METADATA_KEYS:
            raise ValueError(
                f"metadata objects may contain at most {MAX_METADATA_KEYS} keys"
            )
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise ValueError("metadata keys must be strings")
            if len(key) > MAX_METADATA_KEY_LENGTH:
                raise ValueError(
                    "metadata key length may not exceed "
                    f"{MAX_METADATA_KEY_LENGTH} characters"
                )
            _validate_metadata_value(nested_value, depth=depth + 1)
        return

    if isinstance(value, list):
        for item in value:
            _validate_metadata_value(item, depth=depth + 1)
        return

    if value is None or isinstance(value, (str, bool, int)):
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("metadata numbers must be finite")
        return

    raise ValueError(
        "metadata values must be JSON-compatible objects, arrays, or scalars"
    )


class IngestRequest(BaseModel):
    """Request body to ingest a document into the knowledge base."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=settings.INGEST_CONTENT_MAX_LENGTH,
        description="Text content to index.",
    )
    title: str | None = Field(
        default=None, max_length=512, description="Optional document title."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional key-value metadata attached to the document.",
    )

    @field_validator("metadata")
    @classmethod
    def metadata_must_be_reasonable(cls, value: dict[str, Any]) -> dict[str, Any]:
        _validate_metadata_value(value, depth=1)

        try:
            serialized = json.dumps(
                value,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("metadata must be valid JSON") from exc

        if len(serialized) > MAX_METADATA_SERIALIZED_BYTES:
            raise ValueError(
                "serialized metadata may not exceed "
                f"{MAX_METADATA_SERIALIZED_BYTES} bytes"
            )

        return value


class IngestResponse(BaseModel):
    """Response body after document ingestion."""

    document_id: str
    chunk_count: int
    status: str = "ingested"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class ServiceStatus(BaseModel):
    status: str  # "ok" | "error"
    detail: str | None = None


class HealthResponse(BaseModel):
    """Overall health of the application."""

    status: str  # "ok" | "degraded" | "error"
    version: str
    services: dict[str, ServiceStatus]


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------


class ProviderInfo(BaseModel):
    name: str
    default: bool
    available: bool


class ProvidersResponse(BaseModel):
    providers: list[ProviderInfo]


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------


class MessageDetail(BaseModel):
    """A single message inside a session history."""

    role: str
    content: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str


class SessionSummary(BaseModel):
    """Brief session info returned in list responses."""

    session_id: str
    agent_name: str
    created_at: str
    last_accessed_at: str
    message_count: int


class SessionDetail(SessionSummary):
    """Full session info including message history."""

    messages: list[MessageDetail]


# ---------------------------------------------------------------------------
# Knowledge management
# ---------------------------------------------------------------------------


class KnowledgeDocument(BaseModel):
    """Summary of an indexed document in the knowledge base."""

    document_id: str
    title: str | None = None
    chunk_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeListResponse(BaseModel):
    """Paged list of indexed knowledge documents."""

    documents: list[KnowledgeDocument]
    total: int


class KnowledgeSearchRequest(BaseModel):
    """Request body for a semantic knowledge search preview."""

    query: str = Field(..., min_length=1, max_length=2000, description="Search query.")
    limit: int = Field(default=5, ge=1, le=20)


class KnowledgeSearchResult(BaseModel):
    """A single search result chunk from the knowledge base."""

    document_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearchResponse(BaseModel):
    """Search results for a knowledge query."""

    query: str
    results: list[KnowledgeSearchResult]
