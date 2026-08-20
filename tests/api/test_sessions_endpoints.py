"""Tests for session management API endpoints.

The FastAPI lifespan is mocked out so Qdrant / LiteLLM are never contacted.
The bootstrapped ``session_repository`` service is replaced with a fresh
SessionRepository backed by an isolated in-memory SQLite engine.

StaticPool is mandatory: Starlette's TestClient runs the ASGI app in a worker
thread.  SQLite's default SingletonThreadPool gives each thread its OWN
connection (= empty database).  StaticPool forces a single shared connection
so tables created in the test thread are visible to the ASGI worker thread.
"""

import asyncio
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

import doitall.database.models  # noqa: F401 — registers table metadata
from doitall.api.models import ChatRequest
from doitall.commands.executor import CommandResult
from doitall.database.session_repository import SessionRepository
from doitall.models.provider_response import ProviderResponse
from doitall.services.registry import container

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # single shared connection across all threads
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _make_repo(engine) -> SessionRepository:
    """Return a SessionRepository backed by the given in-memory engine."""

    @contextmanager
    def factory():
        with DBSession(engine) as s:
            yield s

    return SessionRepository(session_factory=factory)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo():
    """Fresh isolated SessionRepository per test."""
    engine = _make_test_engine()
    return _make_repo(engine)


@pytest.fixture()
def client(repo):
    """TestClient with lifespan mocked (no Qdrant / LiteLLM)."""
    import doitall.api.routes.chat as chat_mod

    container.clear()
    container.register("session_repository", repo)
    chat_mod._hot_sessions.clear()

    from doitall.api.app import app

    with (
        patch("doitall.api.app.bootstrap", return_value=None),
        patch("doitall.api.app.async_bootstrap", new=AsyncMock(return_value=None)),
        patch("doitall.api.app.cleanup", return_value=None),
        TestClient(app) as c,
    ):
        yield c

    container.clear()


# ---------------------------------------------------------------------------
# GET /v1/sessions
# ---------------------------------------------------------------------------


def test_list_sessions_empty(client):
    resp = client.get("/v1/sessions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_sessions_after_create(client, repo):
    repo.get_or_create("list-sess", agent_name="TestAgent")

    resp = client.get("/v1/sessions")
    assert resp.status_code == 200
    ids = [s["session_id"] for s in resp.json()]
    assert "list-sess" in ids


# ---------------------------------------------------------------------------
# GET /v1/sessions/{session_id}
# ---------------------------------------------------------------------------


def test_get_session_not_found(client):
    resp = client.get("/v1/sessions/does-not-exist")
    assert resp.status_code == 404


def test_get_session_with_messages(client, repo):
    repo.get_or_create("detail-sess")
    repo.append_message("detail-sess", role="user", content="hello")
    repo.append_message("detail-sess", role="assistant", content="hi")

    resp = client.get("/v1/sessions/detail-sess")
    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"] == "detail-sess"
    assert body["message_count"] == 2
    assert len(body["messages"]) == 2
    assert body["messages"][0]["role"] == "user"
    assert body["messages"][1]["role"] == "assistant"


# ---------------------------------------------------------------------------
# DELETE /v1/sessions/{session_id}
# ---------------------------------------------------------------------------


def test_delete_session_not_found(client):
    resp = client.delete("/v1/sessions/no-such-session")
    assert resp.status_code == 404


def test_delete_session_success(client, repo):
    repo.get_or_create("to-delete")

    resp = client.delete("/v1/sessions/to-delete")
    assert resp.status_code == 204

    resp2 = client.get("/v1/sessions/to-delete")
    assert resp2.status_code == 404


def test_delete_session_evicts_hot_cache(client, repo):
    import doitall.api.routes.chat as chat_mod

    chat_mod._hot_sessions["evict-me"] = chat_mod.HotSession(
        service=MagicMock(),
        last_accessed=9999999.0,
    )
    repo.get_or_create("evict-me")

    resp = client.delete("/v1/sessions/evict-me")
    assert resp.status_code == 204
    assert "evict-me" not in chat_mod._hot_sessions


def test_commands_endpoint_lists_builtin_commands(client):
    resp = client.get("/v1/commands")

    assert resp.status_code == 200
    names = {command["name"] for command in resp.json()["commands"]}
    assert "/models" in names
    assert "/thinking" in names


def test_get_chat_service_recreates_cache_when_provider_changes(client, repo):
    import doitall.api.routes.chat as chat_mod

    first_service = MagicMock()
    second_service = MagicMock()

    with patch.object(
        chat_mod._factory,
        "create",
        side_effect=[first_service, second_service],
    ):
        service1, _lock1 = chat_mod._get_chat_service(
            "provider-switch", provider="openai"
        )
        service2, _lock2 = chat_mod._get_chat_service(
            "provider-switch", provider="groq"
        )

    assert service1 is first_service
    assert service2 is second_service
    assert chat_mod._hot_sessions["provider-switch"].provider == "groq"
    session = next(s for s in repo.list_sessions() if s.session_id == "provider-switch")
    assert session.provider == "groq"


def test_get_chat_service_reuses_cache_for_same_provider(client):
    import doitall.api.routes.chat as chat_mod

    service = MagicMock()

    with patch.object(chat_mod._factory, "create", return_value=service) as create:
        service1, _lock1 = chat_mod._get_chat_service(
            "same-provider", provider="openai"
        )
        service2, _lock2 = chat_mod._get_chat_service(
            "same-provider", provider="openai"
        )

    assert service1 is service
    assert service2 is service
    create.assert_called_once()


def test_stream_command_does_not_create_chat_service(client, repo):
    import doitall.api.routes.chat as chat_mod

    executor = MagicMock(spec=["is_command", "execute"])
    executor.is_command.return_value = True
    executor.execute = AsyncMock(return_value=CommandResult(content="Help output"))

    with (
        patch.object(
            chat_mod,
            "_get_command_executor",
            return_value=executor,
        ),
        patch.object(
            chat_mod,
            "_get_chat_service",
        ) as get_chat_service,
    ):
        response = client.post(
            "/v1/chat/stream",
            json={"message": "/help"},
        )

    assert response.status_code == 200
    assert "event: session" in response.text
    assert "Help output" in response.text
    assert "[DONE]" in response.text

    get_chat_service.assert_not_called()
    sessions = repo.list_sessions()
    assert len(sessions) == 1
    assert repo.message_count(sessions[0].session_id) == 2


def test_normal_stream_emits_session_before_tokens(client):
    import doitall.api.routes.chat as chat_mod

    class StreamingService:
        async def stream_chat(self, *_args, **_kwargs):
            yield "hello"

    service = StreamingService()
    chat_mod._hot_sessions["stream-session"] = chat_mod.HotSession(
        service=service,
        last_accessed=9999999.0,
    )

    with (
        patch.object(chat_mod, "_get_command_executor", return_value=None),
        patch.object(
            chat_mod, "_get_chat_service", return_value=(service, asyncio.Lock())
        ),
    ):
        response = client.post(
            "/v1/chat/stream",
            json={"message": "hello", "session_id": "stream-session"},
        )

    assert response.status_code == 200
    assert response.text.index("event: session") < response.text.index("event: token")
    assert '"session_id":"stream-session"' in response.text


@pytest.mark.asyncio
async def test_chat_serializes_concurrent_turns_for_one_session(repo):
    import doitall.api.routes.chat as chat_mod

    active = 0
    maximum_active = 0

    class ConcurrentService:
        async def chat_response(self, *_args, **_kwargs):
            nonlocal active, maximum_active
            active += 1
            maximum_active = max(maximum_active, active)
            await asyncio.sleep(0.02)
            active -= 1
            return ProviderResponse(content="ok")

    service = ConcurrentService()
    container.clear()
    container.register("session_repository", repo)
    chat_mod._hot_sessions.clear()
    chat_mod._hot_sessions["shared-session"] = chat_mod.HotSession(
        service=service,
        last_accessed=9999999.0,
    )

    with (
        patch.object(chat_mod, "_get_command_executor", return_value=None),
        patch.object(
            chat_mod, "_get_chat_service", return_value=(service, asyncio.Lock())
        ),
    ):
        await asyncio.gather(
            chat_mod.chat(ChatRequest(message="one", session_id="shared-session")),
            chat_mod.chat(ChatRequest(message="two", session_id="shared-session")),
        )

    assert maximum_active == 1


def test_session_endpoints_apply_bounded_pagination(client, repo):
    for index in range(3):
        session_id = f"page-{index}"
        repo.get_or_create(session_id)
        repo.append_message(session_id, role="user", content="one")
        repo.append_message(session_id, role="assistant", content="two")

    page = client.get("/v1/sessions", params={"limit": 2, "offset": 1})
    detail = client.get(
        "/v1/sessions/page-1",
        params={"message_limit": 1, "message_offset": 1},
    )

    assert page.status_code == 200
    assert len(page.json()) == 2
    assert all(item["message_count"] == 2 for item in page.json())
    assert detail.status_code == 200
    assert detail.json()["message_count"] == 2
    assert len(detail.json()["messages"]) == 1
