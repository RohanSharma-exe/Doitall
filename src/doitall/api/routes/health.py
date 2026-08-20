"""Health check routes for liveness and dependency readiness."""

import asyncio

from fastapi import APIRouter, Response, status
from loguru import logger
from sqlalchemy.engine import Engine

from doitall.api.models import HealthResponse, ServiceStatus
from doitall.config.settings import settings
from doitall.services.registry import container

router = APIRouter()

HEALTH_CHECK_FAILED = "Health check failed"


def _response_status(services: dict[str, ServiceStatus]) -> str:
    return "ok" if all(s.status == "ok" for s in services.values()) else "degraded"


def _check_database(engine: Engine) -> None:
    """Run the synchronous SQL readiness probe outside the event loop."""
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


@router.get("/health/live", response_model=HealthResponse, tags=["system"])
async def liveness() -> HealthResponse:
    """Return process liveness without checking external dependencies."""
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        services={"api": ServiceStatus(status="ok")},
    )


@router.get("/health/ready", response_model=HealthResponse, tags=["system"])
async def readiness(response: Response) -> HealthResponse:
    """Return readiness based on database, Qdrant, and provider manager checks."""
    services: dict[str, ServiceStatus] = {}

    try:
        client = container.resolve("qdrant_client")
        await client.get_collections()
        services["qdrant"] = ServiceStatus(status="ok")
    except Exception:
        logger.exception("Qdrant readiness check failed")
        services["qdrant"] = ServiceStatus(status="error", detail=HEALTH_CHECK_FAILED)

    try:
        engine = container.resolve("engine")
        await asyncio.to_thread(_check_database, engine)
        services["database"] = ServiceStatus(status="ok")
    except Exception:
        logger.exception("Database readiness check failed")
        services["database"] = ServiceStatus(status="error", detail=HEALTH_CHECK_FAILED)

    try:
        manager = container.resolve("provider_manager")
        manager.default()
        services["providers"] = ServiceStatus(status="ok")
    except Exception:
        logger.exception("Provider readiness check failed")
        services["providers"] = ServiceStatus(
            status="error", detail=HEALTH_CHECK_FAILED
        )

    overall = _response_status(services)
    if overall != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status=overall, version=settings.APP_VERSION, services=services
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application health check",
    tags=["system"],
)
async def health(response: Response) -> HealthResponse:
    """Backward-compatible readiness endpoint."""
    return await readiness(response)
