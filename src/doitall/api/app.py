"""
FastAPI application factory for the Doitall framework.

Usage
-----
Run directly:
    uvicorn doitall.api.app:app --reload

Or via the CLI:
    doitall start
"""

import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from loguru import logger

from doitall.api.routes import chat, commands, health, knowledge, providers, system
from doitall.config.settings import settings
from doitall.core.bootstrap import async_bootstrap, bootstrap, cleanup
from doitall.core.exceptions import DoitallError
from doitall.security.auth import require_metrics_api_key

# In-process fixed-window request limiter. Suitable for single-process deployments;
# use an external store (Redis) for horizontally scaled deployments.
_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_request_counts: dict[str, int] = defaultdict(int)
_last_rate_bucket_cleanup = 0.0
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_BUCKET_CLEANUP_INTERVAL_SECONDS = 60


def _rate_limit_for_path(path: str) -> int | None:
    if path == "/v1/chat" or path == "/v1/chat/stream":
        return settings.CHAT_RATE_LIMIT_PER_MINUTE
    if path == "/v1/knowledge/ingest":
        return settings.INGEST_RATE_LIMIT_PER_MINUTE
    return None


def _rate_limit_key(request: Request) -> str:
    api_key = request.headers.get("x-api-key") or request.headers.get(
        "authorization", ""
    )
    if api_key:
        return f"key:{api_key}"
    host = request.client.host if request.client else "unknown"
    return f"ip:{host}"


def _prune_rate_buckets(now: float) -> None:
    """Remove stale rate-limit buckets to prevent unbounded memory growth."""
    global _last_rate_bucket_cleanup

    if now - _last_rate_bucket_cleanup < _RATE_BUCKET_CLEANUP_INTERVAL_SECONDS:
        return

    cutoff = now - _RATE_LIMIT_WINDOW_SECONDS
    stale_keys = []
    for key, bucket in _rate_buckets.items():
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if not bucket:
            stale_keys.append(key)

    for key in stale_keys:
        del _rate_buckets[key]

    _last_rate_bucket_cleanup = now


def _is_rate_limited(key: str, limit: int, now: float) -> bool:
    _prune_rate_buckets(now)
    bucket = _rate_buckets[key]
    cutoff = now - _RATE_LIMIT_WINDOW_SECONDS
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    if len(bucket) >= limit:
        return True
    bucket.append(now)
    return False


def _request_route_label(request: Request) -> str:
    """Return a low-cardinality route label for metrics and logs."""
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if path and request.url.path.startswith("/v1/") and not path.startswith("/v1/"):
        return f"/v1{path}"
    return path or request.url.path


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Bootstrap the framework on startup and clean up on shutdown."""
    logger.info("Starting Doitall API…")
    bootstrap()  # sync: wire all services into the DI container
    await async_bootstrap()  # async: create Qdrant collections on running loop
    yield
    logger.info("Shutting down Doitall API…")
    cleanup()


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Doitall AI Platform — Build infrastructure once. "
            "Build AI applications forever."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # --- CORS ---
    # `allow_credentials=True` with `allow_origins=["*"]` is invalid per the
    # CORS spec and causes browsers to reject preflight responses.
    # We only enable credentials when the caller has configured explicit origins.
    _allow_credentials = "*" not in settings.CORS_ORIGINS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request ID, request logging, and rate limiting ---
    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.perf_counter()

        limit = _rate_limit_for_path(request.url.path)
        if settings.RATE_LIMIT_ENABLED and limit is not None:
            key = _rate_limit_key(request)
            if _is_rate_limited(f"{request.url.path}:{key}", limit, time.monotonic()):
                logger.bind(request_id=request_id).warning(
                    "Rate limit exceeded path={} key={}",
                    request.url.path,
                    key.split(":", 1)[0],
                )
                response = JSONResponse(
                    status_code=429, content={"detail": "Rate limit exceeded"}
                )
                response.headers["X-Request-ID"] = request_id
                return response

        bound_logger = logger.bind(request_id=request_id)
        try:
            response = await call_next(request)
        except Exception:
            bound_logger.exception("Unhandled request error path={}", request.url.path)
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        route_label = _request_route_label(request)
        _request_counts[f"{request.method} {route_label} {response.status_code}"] += 1
        response.headers["X-Request-ID"] = request_id
        bound_logger.info(
            "HTTP request method={} path={} status={} duration_ms={:.2f}",
            request.method,
            route_label,
            response.status_code,
            duration_ms,
        )
        return response

    # --- Global error handler for domain exceptions ---
    @app.exception_handler(DoitallError)
    async def doitall_error_handler(
        request: Request,
        exc: DoitallError,
    ) -> JSONResponse:
        logger.warning(f"Domain error on {request.url}: {exc}")
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )

    # --- Routes ---
    app.include_router(health.router, prefix="/v1")
    app.include_router(chat.router, prefix="/v1")
    app.include_router(knowledge.router, prefix="/v1")
    app.include_router(providers.router, prefix="/v1")
    app.include_router(commands.router, prefix="/v1")
    app.include_router(system.router, prefix="/v1")

    @app.get(
        "/metrics",
        include_in_schema=False,
        dependencies=[Depends(require_metrics_api_key)],
    )
    async def metrics():
        lines = ["# TYPE doitall_http_requests_total counter"]
        for key, count in sorted(_request_counts.items()):
            method, path, status_code = key.rsplit(" ", 2)
            route = method.split(" ", 1)[1] if " " in method else path
            verb = method.split(" ", 1)[0]
            lines.append(
                f'doitall_http_requests_total{{method="{verb}",path="{route}",status="{status_code}"}} {count}'
            )
        return Response("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }

    return app


# ---------------------------------------------------------------------------
# Module-level app instance (used by uvicorn)
# ---------------------------------------------------------------------------

app = create_app()
