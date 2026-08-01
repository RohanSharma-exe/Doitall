from collections import deque
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session as DBSession
from sqlmodel import SQLModel, create_engine

from doitall.api import app as app_mod
from doitall.api.app import create_app
from doitall.database.session_repository import SessionRepository
from doitall.services.registry import container


def _make_repo() -> SessionRepository:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    @contextmanager
    def factory():
        with DBSession(engine) as session:
            yield session

    return SessionRepository(session_factory=factory)


def test_rate_limit_prunes_stale_buckets():
    app_mod._rate_buckets.clear()
    app_mod._last_rate_bucket_cleanup = 0.0
    app_mod._rate_buckets["stale"] = deque([1.0])
    app_mod._rate_buckets["active"] = deque([125.0])

    app_mod._prune_rate_buckets(130.0)

    assert "stale" not in app_mod._rate_buckets
    assert "active" in app_mod._rate_buckets


def test_route_label_prefers_fastapi_route_template():
    request = SimpleNamespace(
        scope={"route": SimpleNamespace(path="/v1/sessions/{session_id}")},
        url=SimpleNamespace(path="/v1/sessions/abc"),
    )

    assert app_mod._request_route_label(request) == "/v1/sessions/{session_id}"


def test_metrics_use_route_templates_for_dynamic_paths():
    app_mod._request_counts.clear()
    container.clear()
    container.register("session_repository", _make_repo())

    with (
        patch("doitall.api.app.bootstrap", return_value=None),
        patch("doitall.api.app.async_bootstrap", new=AsyncMock(return_value=None)),
        patch("doitall.api.app.cleanup", return_value=None),
    ):
        app = create_app()
        with TestClient(app) as client:
            client.get("/v1/sessions/one")
            client.get("/v1/sessions/two")
            metrics = client.get("/metrics")

    container.clear()

    assert metrics.status_code == 200
    assert 'path="/v1/sessions/{session_id}"' in metrics.text
    assert 'path="/v1/sessions/one"' not in metrics.text
    assert 'path="/v1/sessions/two"' not in metrics.text
