"""Health check routes for liveness and dependency readiness."""
from fastapi import APIRouter, Response, status

from doitall.api.models import HealthResponse, ServiceStatus
from doitall.config.settings import settings
from doitall.services.registry import container

router = APIRouter()


def _response_status(services: dict[str, ServiceStatus]) -> str:
    return "ok" if all(s.status == "ok" for s in services.values()) else "degraded"


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
    except Exception as exc:
        services["qdrant"] = ServiceStatus(status="error", detail=str(exc))

    try:
        from sqlalchemy import text

        engine = container.resolve("engine")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        services["database"] = ServiceStatus(status="ok")
    except Exception as exc:
        services["database"] = ServiceStatus(status="error", detail=str(exc))

    try:
        manager = container.resolve("provider_manager")
        manager.default()
        services["providers"] = ServiceStatus(status="ok")
    except Exception as exc:
        services["providers"] = ServiceStatus(status="error", detail=str(exc))

    overall = _response_status(services)
    if overall != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(status=overall, version=settings.APP_VERSION, services=services)


@router.get("/health", response_model=HealthResponse, summary="Application health check", tags=["system"])
async def health(response: Response) -> HealthResponse:
    """Backward-compatible readiness endpoint."""
    return await readiness(response)
