"""Chat route — one-turn and session-aware chat via the Doitall runtime."""
import time
import uuid
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from doitall.agent.agent import Agent
from doitall.api.models import (
    ChatRequest,
    ChatResponse,
    MessageDetail,
    SessionDetail,
    SessionSummary,
)
from doitall.config.settings import settings
from doitall.core.exceptions import DoitallError
from doitall.database.session_repository import SessionRepository
from doitall.runtime.runtime_factory import RuntimeFactory
from doitall.security.auth import require_api_key
from doitall.services.chat_service import ChatService
from doitall.services.conversation_service import ConversationService

router = APIRouter()

_factory = RuntimeFactory()
_lock = Lock()

# ---------------------------------------------------------------------------
# Hot session cache — avoids a DB round-trip on every turn for active chats.
# Stores (ChatService, last_accessed_timestamp).  The DB is the source of
# truth; this cache is purely a performance optimisation.
# ---------------------------------------------------------------------------
_hot_sessions: dict[str, tuple[ChatService, float]] = {}

# Shared repository instance (one per process)
_repo = SessionRepository()


def _evict_expired() -> None:
    """Evict sessions that have been idle longer than SESSION_TTL_SECONDS."""
    now = time.monotonic()
    ttl = settings.SESSION_TTL_SECONDS
    expired = [sid for sid, (_, ts) in _hot_sessions.items() if now - ts > ttl]
    for sid in expired:
        del _hot_sessions[sid]


def _make_chat_service(session_id: str, provider: str | None = None) -> ChatService:
    """Create a ChatService wired to a DB-backed ConversationService."""
    agent = Agent(
        name="Doitall",
        system_prompt="You are a helpful AI assistant.",
    )
    # Ensure session row exists in DB
    _repo.get_or_create(
        session_id=session_id,
        agent_name=agent.name,
        system_prompt=agent.system_prompt,
        provider=provider,
    )
    conversation_service = ConversationService(
        session_id=session_id,
        repository=_repo,
    )
    return _factory.create(agent, conversation_service=conversation_service)


def _get_chat_service(session_id: str, provider: str | None = None) -> ChatService:
    """Return a hot-cached ChatService, creating one if needed."""
    with _lock:
        _evict_expired()
        if session_id not in _hot_sessions:
            service = _make_chat_service(session_id, provider)
            _hot_sessions[session_id] = (service, time.monotonic())
        else:
            # Refresh timestamp on every hit
            service, _ = _hot_sessions[session_id]
            _hot_sessions[session_id] = (service, time.monotonic())

        _repo.touch(session_id)
        return _hot_sessions[session_id][0]


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a chat message",
    tags=["chat"],
    dependencies=[Depends(require_api_key)],
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a single message and receive an AI response.

    The agent has access to all registered skills and will use tool-calling
    automatically when needed.  Conversation history is persisted to the
    database — sessions survive server restarts.

    Sessions are kept hot in memory for ``SESSION_TTL_SECONDS`` (default 1 h)
    after the last message and are evicted automatically.
    """
    session_id = request.session_id or str(uuid.uuid4())

    try:
        service = _get_chat_service(session_id, provider=request.provider)
        response_text = await service.chat(
            request.message,
            provider=request.provider,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown provider: {request.provider}",
        ) from exc
    except DoitallError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc

    return ChatResponse(
        response=response_text,
        session_id=session_id,
    )


@router.post(
    "/chat/stream",
    summary="Stream a chat response",
    tags=["chat"],
    dependencies=[Depends(require_api_key)],
)
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream a chat response as Server-Sent Events."""
    session_id = request.session_id or str(uuid.uuid4())

    async def event_source():
        try:
            service = _get_chat_service(session_id, provider=request.provider)
            yield f"event: session\ndata: {session_id}\n\n"
            async for chunk in service.stream_chat(request.message, provider=request.provider):
                safe_chunk = chunk.replace("\r", " ").replace("\n", "\ndata: ")
                yield f"data: {safe_chunk}\n\n"
            yield "event: done\ndata: [DONE]\n\n"
        except KeyError:
            yield f"event: error\ndata: Unknown provider: {request.provider}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {str(exc)}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Session management endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/sessions",
    response_model=list[SessionSummary],
    summary="List all sessions",
    tags=["sessions"],
    dependencies=[Depends(require_api_key)],
)
def list_sessions() -> list[SessionSummary]:
    """Return a summary of all sessions ordered by most recently active."""
    sessions = _repo.list_sessions()
    return [
        SessionSummary(
            session_id=s.session_id,
            agent_name=s.agent_name,
            created_at=s.created_at.isoformat(),
            last_accessed_at=s.last_accessed_at.isoformat(),
            message_count=_repo.message_count(s.session_id),
        )
        for s in sessions
    ]


@router.get(
    "/sessions/{session_id}",
    response_model=SessionDetail,
    summary="Get session details",
    tags=["sessions"],
    dependencies=[Depends(require_api_key)],
)
def get_session(session_id: str) -> SessionDetail:
    """Return full session metadata and complete message history."""
    if not _repo.exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    sessions = _repo.list_sessions()
    session = next((s for s in sessions if s.session_id == session_id), None)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = _repo.get_messages(session_id)
    return SessionDetail(
        session_id=session.session_id,
        agent_name=session.agent_name,
        created_at=session.created_at.isoformat(),
        last_accessed_at=session.last_accessed_at.isoformat(),
        message_count=len(messages),
        messages=[
            MessageDetail(
                role=m.role,
                content=m.content,
                tool_calls=m.get_tool_calls(),
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
    )


@router.delete(
    "/sessions/{session_id}",
    status_code=204,
    summary="Delete a session",
    tags=["sessions"],
    dependencies=[Depends(require_api_key)],
)
def delete_session(session_id: str) -> None:
    """Delete a session and its entire message history. Returns 204 on success."""
    # Evict from hot cache first
    with _lock:
        _hot_sessions.pop(session_id, None)

    deleted = _repo.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
