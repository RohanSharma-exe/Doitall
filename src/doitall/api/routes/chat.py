"""Chat route — one-turn and session-aware chat via the Doitall runtime."""
import uuid

from fastapi import APIRouter, Depends, HTTPException

from doitall.agent.agent import Agent
from doitall.api.models import ChatRequest, ChatResponse
from doitall.core.exceptions import DoitallError
from doitall.runtime.runtime_factory import RuntimeFactory
from doitall.security.auth import require_api_key
from doitall.services.chat_service import ChatService

router = APIRouter()

_factory = RuntimeFactory()
_sessions: dict[str, ChatService] = {}


def _make_chat_service() -> ChatService:
    agent = Agent(
        name="Doitall",
        system_prompt="You are a helpful AI assistant.",
    )
    return _factory.create(agent)


def _get_chat_service(session_id: str) -> ChatService:
    if session_id not in _sessions:
        _sessions[session_id] = _make_chat_service()

    return _sessions[session_id]


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

    The agent has access to all registered skills (calculator, filesystem, etc.)
    and will use tool-calling automatically when needed.
    """
    session_id = request.session_id or str(uuid.uuid4())

    try:
        service = _get_chat_service(session_id)
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
