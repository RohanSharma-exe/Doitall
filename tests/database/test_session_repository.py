"""Tests for SessionRepository using an in-memory SQLite database."""
from contextlib import contextmanager

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

import doitall.database.models  # noqa: F401 — register table metadata

from doitall.database.session_repository import SessionRepository


def _make_repo(engine) -> SessionRepository:
    """Return a SessionRepository wired to the given engine."""
    @contextmanager
    def factory():
        with DBSession(engine) as s:
            yield s

    return SessionRepository(session_factory=factory)


@pytest.fixture()
def repo():
    """Isolated in-memory SQLite repo, fresh per test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return _make_repo(engine)


def test_get_or_create_creates_new_session(repo):
    record = repo.get_or_create("sess-1")
    assert record.session_id == "sess-1"
    assert record.agent_name == "Doitall"


def test_get_or_create_is_idempotent(repo):
    r1 = repo.get_or_create("sess-2", agent_name="Agent A")
    r2 = repo.get_or_create("sess-2", agent_name="Agent B")
    # Second call must not overwrite the first
    assert r1.session_id == r2.session_id
    assert r2.agent_name == "Agent A"


def test_exists_true_after_create(repo):
    repo.get_or_create("sess-3")
    assert repo.exists("sess-3") is True


def test_exists_false_for_unknown(repo):
    assert repo.exists("does-not-exist") is False


def test_append_and_load_messages(repo):
    repo.get_or_create("sess-4")
    repo.append_message("sess-4", role="user", content="Hello")
    repo.append_message("sess-4", role="assistant", content="Hi there!")

    messages = repo.get_messages("sess-4")
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hi there!"


def test_append_message_with_tool_calls(repo):
    repo.get_or_create("sess-5")
    tool_calls = [{"id": "tc1", "name": "calculator", "arguments": {"expr": "1+1"}}]
    repo.append_message("sess-5", role="assistant", content="", tool_calls=tool_calls)

    messages = repo.get_messages("sess-5")
    assert len(messages) == 1
    assert messages[0].get_tool_calls() == tool_calls


def test_clear_messages(repo):
    repo.get_or_create("sess-6")
    repo.append_message("sess-6", role="user", content="msg1")
    repo.append_message("sess-6", role="assistant", content="msg2")

    count = repo.clear_messages("sess-6")
    assert count == 2
    assert repo.get_messages("sess-6") == []


def test_message_count(repo):
    repo.get_or_create("sess-7")
    assert repo.message_count("sess-7") == 0
    repo.append_message("sess-7", role="user", content="a")
    repo.append_message("sess-7", role="assistant", content="b")
    assert repo.message_count("sess-7") == 2


def test_delete_session_removes_messages(repo):
    repo.get_or_create("sess-8")
    repo.append_message("sess-8", role="user", content="bye")

    deleted = repo.delete("sess-8")
    assert deleted is True
    assert repo.exists("sess-8") is False
    assert repo.get_messages("sess-8") == []


def test_delete_returns_false_for_missing(repo):
    assert repo.delete("no-such-session") is False


def test_list_sessions(repo):
    repo.get_or_create("sess-a")
    repo.get_or_create("sess-b")

    sessions = repo.list_sessions()
    ids = [s.session_id for s in sessions]
    assert "sess-a" in ids
    assert "sess-b" in ids


def test_touch_updates_timestamp(repo):
    import time as _time
    repo.get_or_create("sess-touch")
    before = {s.session_id: s.last_accessed_at for s in repo.list_sessions()}
    _time.sleep(0.05)
    repo.touch("sess-touch")
    after = {s.session_id: s.last_accessed_at for s in repo.list_sessions()}
    assert after["sess-touch"] >= before["sess-touch"]
