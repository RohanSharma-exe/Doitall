"""Chat route — one-turn and session-aware chat via the Doitall runtime."""

import asyncio
import time
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from threading import Lock

import orjson
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from loguru import logger

from doitall.agent.agent import Agent
from doitall.api.errors import CHAT_FAILED, STREAM_FAILED
from doitall.api.models import (
    ChatRequest,
    ChatResponse,
    MessageDetail,
    SessionDetail,
    SessionSummary,
)
from doitall.commands import default_registry
from doitall.commands.executor import SlashCommandExecutor
from doitall.config.settings import settings
from doitall.core.exceptions import DoitallError
from doitall.database.session_repository import SessionRepository
from doitall.models.stream import StreamEvent
from doitall.runtime.runtime_factory import RuntimeFactory
from doitall.security.auth import require_api_key
from doitall.services.chat_service import ChatService
from doitall.services.conversation_service import ConversationService
from doitall.services.registry import container

router = APIRouter()

_factory = RuntimeFactory()
_lock = Lock()

# ---------------------------------------------------------------------------
# Hot session cache — avoids a DB round-trip on every turn for active chats.
# Stores ChatService plus metadata needed to safely refresh/recreate hot sessions.
# The DB is the source of truth; this cache is purely a performance optimisation.
# ---------------------------------------------------------------------------


@dataclass
class HotSession:
    service: ChatService
    last_accessed: float
    provider: str | None = None
    turn_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


_hot_sessions: dict[str, HotSession] = {}

# Fallback repository for direct route-unit tests that do not run bootstrap.
_repo = SessionRepository()


def _get_repo() -> SessionRepository:
    """Return the bootstrapped session repository when available."""
    if container.has("session_repository"):
        repository = container.resolve("session_repository")
        if not isinstance(repository, SessionRepository):
            raise TypeError("Registered session_repository has an invalid type.")
        return repository

    return _repo


def _get_command_executor() -> SlashCommandExecutor | None:
    """Return a slash command executor when runtime services are ready."""
    if not (container.has("provider_manager") and container.has("skill_registry")):
        return None
    return SlashCommandExecutor(
        default_registry(),
        container.resolve("provider_manager"),
        container.resolve("skill_registry"),
        container.resolve("skill_manager"),
    )


def _evict_expired() -> None:
    """Evict sessions that have been idle longer than SESSION_TTL_SECONDS."""
    now = time.monotonic()
    ttl = settings.SESSION_TTL_SECONDS
    expired = [
        sid
        for sid, hot_session in _hot_sessions.items()
        if now - hot_session.last_accessed > ttl
    ]
    for sid in expired:
        del _hot_sessions[sid]


def _make_chat_service(session_id: str, provider: str | None = None) -> ChatService:
    """Create a ChatService wired to a DB-backed ConversationService."""
    agent = Agent(
        name="Doitall",
        system_prompt="You are a helpful AI assistant.",
    )
    repo = _get_repo()
    # Ensure session row exists in DB
    repo.get_or_create(
        session_id=session_id,
        agent_name=agent.name,
        system_prompt=agent.system_prompt,
        provider=provider,
    )
    conversation_service = ConversationService(
        session_id=session_id,
        repository=repo,
    )
    return _factory.create(agent, conversation_service=conversation_service)


def _get_chat_service(
    session_id: str, provider: str | None = None
) -> tuple[ChatService, asyncio.Lock]:
    """Return a hot-cached (ChatService, turn_lock) pair, creating one if needed.

    The lock is returned together with the service in a single atomic operation
    to avoid the TOCTOU race where the session could be evicted between
    ``_get_chat_service`` and a separate ``_get_turn_lock`` call (BUG-N002).
    """
    with _lock:
        _evict_expired()
        hot_session = _hot_sessions.get(session_id)
        now = time.monotonic()
        if hot_session is None or hot_session.provider != provider:
            service = _make_chat_service(session_id, provider)
            _hot_sessions[session_id] = HotSession(
                service=service,
                last_accessed=now,
                provider=provider,
                turn_lock=hot_session.turn_lock if hot_session else asyncio.Lock(),
            )
            if hot_session is not None:
                _get_repo().update_provider(session_id, provider)
        else:
            hot_session.last_accessed = now

        _get_repo().touch(session_id)
        entry = _hot_sessions[session_id]
        return entry.service, entry.turn_lock


def _persist_command_result(
    session_id: str,
    command: str,
    result: str,
    provider: str | None,
) -> None:
    """Persist command exchanges so every returned session ID is usable."""
    repo = _get_repo()
    repo.get_or_create(session_id=session_id, provider=provider)
    repo.append_message(session_id, role="user", content=command)
    repo.append_message(session_id, role="assistant", content=result)
    repo.touch(session_id)


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

    command_executor = _get_command_executor()
    if command_executor and command_executor.is_command(request.message):
        command_result = await command_executor.execute(request.message)
        if command_result is not None:
            await asyncio.to_thread(
                _persist_command_result,
                session_id,
                request.message,
                command_result.content,
                request.provider,
            )
            return ChatResponse(
                response=command_result.content,
                message={"role": "assistant", "content": command_result.content},
                session_id=session_id,
            )

    try:
        service, turn_lock = await asyncio.to_thread(
            _get_chat_service, session_id, request.provider
        )
        async with turn_lock:
            response = await service.chat_response(
                request.message,
                provider=request.provider,
                model=request.model,
            )
    except KeyError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown provider: {request.provider}",
        ) from exc
    except DoitallError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Chat request failed session_id={}", session_id)
        raise HTTPException(status_code=500, detail=CHAT_FAILED) from exc

    return ChatResponse(
        response=response.content,
        message={"role": "assistant", "content": response.content},
        model=response.model or request.model,
        usage_tokens=response.usage_tokens,
        session_id=session_id,
    )


@router.post(
    "/chat/stream",
    summary="Stream a chat response",
    tags=["chat"],
    dependencies=[Depends(require_api_key)],
)
async def chat_stream(http_request: Request, request: ChatRequest) -> StreamingResponse:
    """Stream a chat response as Server-Sent Events."""
    session_id = request.session_id or str(uuid.uuid4())

    def sse(event: StreamEvent) -> str:
        payload = orjson.dumps(event.model_dump()).decode("utf-8")
        return f"id: {event.id}\nevent: {event.event}\ndata: {payload}\n\n"

    async def event_source() -> AsyncIterator[str]:
        yield sse(
            StreamEvent(
                event="session",
                data={"session_id": session_id},
            )
        )
        try:
            command_executor = _get_command_executor()
            if command_executor and command_executor.is_command(request.message):
                command_result = await command_executor.execute(request.message)

                if command_result is not None:
                    await asyncio.to_thread(
                        _persist_command_result,
                        session_id,
                        request.message,
                        command_result.content,
                        request.provider,
                    )
                    yield sse(
                        StreamEvent(
                            event="token",
                            data={"text": command_result.content},
                        )
                    )

                    yield sse(
                        StreamEvent(
                            event="done",
                            data={"message": "[DONE]"},
                        )
                    )

                    return
            service, turn_lock = await asyncio.to_thread(
                _get_chat_service,
                session_id,
                request.provider,
            )
            # BUG-N012: Track client disconnects so we stop generating tokens
            # when the client has gone away, avoiding wasted LLM spend.
            async with turn_lock:
                async for chunk in service.stream_chat(
                    request.message, provider=request.provider, model=request.model
                ):
                    if await http_request.is_disconnected():
                        logger.info(
                            "Client disconnected mid-stream session_id={}", session_id
                        )
                        return
                    yield sse(StreamEvent(event="token", data={"text": chunk}))
            yield sse(StreamEvent(event="done", data={"message": "[DONE]"}))
        except KeyError:
            yield sse(
                StreamEvent(
                    event="error",
                    data={"code": "unknown_provider", "message": "Unknown provider."},
                )
            )
        except Exception:
            logger.exception("Chat stream failed session_id={}", session_id)
            yield sse(
                StreamEvent(
                    event="error",
                    data={"code": "stream_failed", "message": STREAM_FAILED},
                )
            )

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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
def list_sessions(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[SessionSummary]:
    """Return a bounded page of sessions ordered by most recently active."""
    repo = _get_repo()
    sessions = repo.list_sessions(limit=limit, offset=offset)
    counts = repo.message_counts([session.session_id for session in sessions])
    return [
        SessionSummary(
            session_id=s.session_id,
            agent_name=s.agent_name,
            created_at=s.created_at.isoformat(),
            last_accessed_at=s.last_accessed_at.isoformat(),
            message_count=counts.get(s.session_id, 0),
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
def get_session(
    session_id: str,
    message_limit: int = Query(default=100, ge=1, le=500),
    message_offset: int = Query(default=0, ge=0),
) -> SessionDetail:
    """Return session metadata and a bounded page of message history."""
    repo = _get_repo()
    session = repo.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    message_count = repo.message_count(session_id)
    messages = repo.get_messages(
        session_id,
        limit=message_limit,
        offset=message_offset,
    )
    return SessionDetail(
        session_id=session.session_id,
        agent_name=session.agent_name,
        created_at=session.created_at.isoformat(),
        last_accessed_at=session.last_accessed_at.isoformat(),
        message_count=message_count,
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
async def delete_session(session_id: str) -> None:
    """Delete a session and its entire message history. Returns 204 on success.

    BUG-N008: We acquire the session's turn lock before touching the DB so that
    any in-flight stream for this session has finished appending messages before
    we delete the row.  The lock is held just long enough to mark the session as
    "being deleted"; the heavy DB call happens after releasing.
    """
    # Atomically remove the session from the hot cache while holding the
    # process-wide cache lock, and grab a reference to its turn_lock.
    turn_lock: asyncio.Lock | None = None
    with _lock:
        hot_session = _hot_sessions.pop(session_id, None)
        if hot_session is not None:
            turn_lock = hot_session.turn_lock

    if turn_lock is not None:
        # Wait for any in-flight turn to complete before deleting from the DB.
        async with turn_lock:
            pass  # Lock acquired — no active turn is running.

    deleted = _get_repo().delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
