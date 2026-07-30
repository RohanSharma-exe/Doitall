"""Chat route — one-turn and session-aware chat via the Doitall runtime."""
import uuid

from fastapi import APIRouter, HTTPException

from doitall.agent.agent import Agent
from doitall.api.models import ChatRequest, ChatResponse
from doitall.core.exceptions import DoitallError
from doitall.runtime.runtime_factory import RuntimeFactory

router = APIRouter()

# Each request currently gets a fresh ChatService (stateless per-request).
# Session persistence (multi-turn via session_id) is a future extension.
_factory = RuntimeFactory()


def _make_chat_service():
    agent = Agent(
        name="Doitall",
        system_prompt="You are a helpful AI assistant.",
    )
    return _factory.create(agent)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a chat message",
    tags=["chat"],
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a single message and receive an AI response.

    The agent has access to all registered skills (calculator, filesystem, etc.)
    and will use tool-calling automatically when needed.
    """
    try:
        service = _make_chat_service()
        response_text = await service.chat(request.message)
    except DoitallError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc

    return ChatResponse(
        response=response_text,
        session_id=request.session_id or str(uuid.uuid4()),
    )
