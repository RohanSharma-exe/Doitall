"""Tests for session management API endpoints.

The FastAPI lifespan is mocked out so Qdrant / LiteLLM are never contacted.
The route's module-level ``_repo`` is replaced with a fresh SessionRepository
backed by an isolated in-memory SQLite engine — no monkeypatching required.

StaticPool is mandatory: Starlette's TestClient runs the ASGI app in a worker
thread.  SQLite's default SingletonThreadPool gives each thread its OWN
connection (= empty database).  StaticPool forces a single shared connection
so tables created in the test thread are visible to the ASGI worker thread.
"""

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

import doitall.database.models  # noqa: F401 — registers table metadata
from doitall.database.session_repository import SessionRepository

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

    chat_mod._repo = repo
    chat_mod._hot_sessions.clear()

    from doitall.api.app import app

    with (
        patch("doitall.api.app.bootstrap", return_value=None),
        patch("doitall.api.app.async_bootstrap", new=AsyncMock(return_value=None)),
        patch("doitall.api.app.cleanup", return_value=None),
        TestClient(app) as c,
    ):
        yield c


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

    chat_mod._hot_sessions["evict-me"] = (MagicMock(), 9999999.0)
    repo.get_or_create("evict-me")

    resp = client.delete("/v1/sessions/evict-me")
    assert resp.status_code == 204
    assert "evict-me" not in chat_mod._hot_sessions
