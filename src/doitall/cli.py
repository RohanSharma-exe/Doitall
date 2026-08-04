"""Typer CLI commands module for Doitall application management."""

import asyncio

import typer
import uvicorn
from rich import print
from rich.table import Table

from doitall.chat import run_chat
from doitall.config.settings import settings

app = typer.Typer(
    name="doitall",
    help="Doitall AI Platform",
    no_args_is_help=True,
)



@app.command()
def version() -> None:
    """Show application version."""
    print(f"[green]{settings.APP_NAME}[/green] v{settings.APP_VERSION}")


@app.command()
def doctor() -> None:
    """Check the application environment and connectivity."""
    print("[bold green]Running diagnostics…[/bold green]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Check", style="dim", width=24)
    table.add_column("Status")
    table.add_column("Detail")

    def _ok(check: str, detail: str = "") -> None:
        table.add_row(check, "[green]OK[/green]", detail)

    def _fail(check: str, detail: str = "") -> None:
        table.add_row(check, "[red]FAIL[/red]", detail)

    def _warn(check: str, detail: str = "") -> None:
        table.add_row(check, "[yellow]WARN[/yellow]", detail)

    # --- Python / config ---
    import sys

    _ok("Python", f"{sys.version.split()[0]}")
    _ok("App", f"{settings.APP_NAME} v{settings.APP_VERSION}")
    _ok("Environment", settings.ENVIRONMENT)

    # --- Qdrant ---
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )
        client.get_collections()
        _ok("Qdrant", settings.QDRANT_URL)
    except Exception as exc:
        _fail("Qdrant", str(exc))

    # --- Database ---
    try:
        from sqlalchemy import create_engine, text

        eng = create_engine(settings.DATABASE_URL)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        _ok("Database", settings.DATABASE_URL)
    except Exception as exc:
        _fail("Database", str(exc))

    # --- API keys ---
    key_checks = [
        ("OPENAI_API_KEY", "OpenAI"),
        ("GEMINI_API_KEY", "Gemini"),
        ("ANTHROPIC_API_KEY", "Anthropic"),
        ("GROQ_API_KEY", "Groq"),
    ]
    for attr, label in key_checks:
        key = getattr(settings, attr, "")
        if key:
            _ok(f"{label} Key", "configured")
        else:
            _warn(f"{label} Key", "not set")

    print(table)


@app.command()
def start(
    host: str = typer.Option(None, help="Host to bind (overrides settings)."),
    port: int = typer.Option(None, help="Port to bind (overrides settings)."),
    reload: bool = typer.Option(False, help="Enable hot-reload for development."),
) -> None:
    """Start the Doitall REST API server."""
    _host = host or settings.API_HOST
    _port = port or settings.API_PORT

    print(
        f"[bold green]Starting {settings.APP_NAME} v{settings.APP_VERSION}[/bold green] "
        f"on [cyan]http://{_host}:{_port}[/cyan]"
    )
    print(f"  Docs     → [link]http://{_host}:{_port}/docs[/link]")
    print(f"  Health   → [link]http://{_host}:{_port}/v1/health[/link]")

    uvicorn.run(
        "doitall.api.app:app",
        host=_host,
        port=_port,
        reload=reload,
        log_level=settings.LOG_LEVEL.lower(),
    )


@app.command()
def chat() -> None:
    """Start an interactive chat session in the terminal."""
    asyncio.run(run_chat())


if __name__ == "__main__":
    app()
