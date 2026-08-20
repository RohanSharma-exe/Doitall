from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Response, status

import doitall.api.routes.health as health_routes


@pytest.mark.asyncio
async def test_readiness_reports_healthy_dependencies():
    qdrant_client = MagicMock()
    qdrant_client.get_collections = AsyncMock(return_value=[])

    connection = MagicMock()
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection

    provider_manager = MagicMock()
    provider_manager.default.return_value = MagicMock()

    dependencies = {
        "qdrant_client": qdrant_client,
        "engine": engine,
        "provider_manager": provider_manager,
    }
    response = Response()

    with patch.object(
        health_routes.container,
        "resolve",
        side_effect=dependencies.__getitem__,
    ):
        result = await health_routes.readiness(response)

    assert response.status_code == status.HTTP_200_OK
    assert result.status == "ok"
    assert all(service.status == "ok" for service in result.services.values())
    qdrant_client.get_collections.assert_awaited_once_with()
    connection.execute.assert_called_once()
    provider_manager.default.assert_called_once_with()


@pytest.mark.asyncio
async def test_readiness_sanitizes_errors_and_logs_full_exceptions():
    dependency_errors = {
        "qdrant_client": RuntimeError("qdrant token=secret-qdrant"),
        "engine": RuntimeError("database password=secret-database"),
        "provider_manager": RuntimeError("provider key=secret-provider"),
    }

    def fail_resolve(name: str):
        raise dependency_errors[name]

    log_output = StringIO()
    sink_id = health_routes.logger.add(
        log_output,
        format="{message}\n{exception}",
        backtrace=False,
        diagnose=False,
    )
    response = Response()

    try:
        with patch.object(
            health_routes.container,
            "resolve",
            side_effect=fail_resolve,
        ):
            result = await health_routes.readiness(response)
    finally:
        health_routes.logger.remove(sink_id)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert result.status == "degraded"
    assert {service.detail for service in result.services.values()} == {
        health_routes.HEALTH_CHECK_FAILED
    }

    public_response = result.model_dump_json()
    logs = log_output.getvalue()
    for error in dependency_errors.values():
        assert str(error) not in public_response
        assert str(error) in logs
