"""
REST API request and response models for the Doitall framework.
"""
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Request body for a chat turn."""

    message: str = Field(..., description="The user's message.")
    provider: str | None = Field(
        default=None,
        description="Override the default provider (e.g. 'openai', 'groq').",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional session identifier for tracking.",
    )


class ChatResponse(BaseModel):
    """Response body from a chat turn."""

    response: str
    model: str | None = None
    session_id: str | None = None


# ---------------------------------------------------------------------------
# Knowledge ingestion
# ---------------------------------------------------------------------------


class IngestRequest(BaseModel):
    """Request body to ingest a document into the knowledge base."""

    content: str = Field(..., description="Text content to index.")
    title: str | None = Field(default=None, description="Optional document title.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional key-value metadata attached to the document.",
    )


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
    tool_calls: list[dict] = []
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
