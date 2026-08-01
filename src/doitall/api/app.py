"""
FastAPI application factory for the Doitall framework.

Usage
-----
Run directly:
    uvicorn doitall.api.app:app --reload

Or via the CLI:
    doitall start
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from doitall.config.settings import settings
from doitall.core.bootstrap import async_bootstrap, bootstrap, cleanup
from doitall.core.exceptions import DoitallError

from doitall.api.routes import chat, health, knowledge, providers


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Bootstrap the framework on startup and clean up on shutdown."""
    logger.info("Starting Doitall API…")
    bootstrap()            # sync: wire all services into the DI container
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
