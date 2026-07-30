"""Health check route — performs real connectivity checks."""
from fastapi import APIRouter

from doitall.config.settings import settings
from doitall.api.models import HealthResponse, ServiceStatus
from doitall.services.registry import container

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application health check",
    tags=["system"],
)
async def health() -> HealthResponse:
    """Return the live health status of each backing service."""
    services: dict[str, ServiceStatus] = {}

    # --- Qdrant ---
    try:
        client = container.resolve("qdrant_client")
        client.get_collections()
        services["qdrant"] = ServiceStatus(status="ok")
    except Exception as exc:
        services["qdrant"] = ServiceStatus(status="error", detail=str(exc))

    # --- Database ---
    try:
        from sqlalchemy import text
        engine = container.resolve("engine")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        services["database"] = ServiceStatus(status="ok")
    except Exception as exc:
        services["database"] = ServiceStatus(status="error", detail=str(exc))

    # --- Providers ---
    try:
        manager = container.resolve("provider_manager")
        manager.default()
        services["providers"] = ServiceStatus(status="ok")
    except Exception as exc:
        services["providers"] = ServiceStatus(status="error", detail=str(exc))

    overall = (
        "ok"
        if all(s.status == "ok" for s in services.values())
        else "degraded"
    )

    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        services=services,
    )
