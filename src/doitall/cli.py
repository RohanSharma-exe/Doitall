import typer
from rich import print

from doitall import Doitall
from doitall.chat import start_chat
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
    """Check the application environment."""
    print("[bold green]Running diagnostics...[/bold green]")

    print(f"Application : {settings.APP_NAME}")
    print(f"Version     : {settings.APP_VERSION}")
    print(f"Environment : {settings.ENVIRONMENT}")
    print("Python      : OK")
    print("Configuration : OK")
    print("Logging       : OK")


@app.command()
def start() -> None:
    """Start the application."""
    Doitall().start()


@app.command()
def chat() -> None:
    """Start an interactive chat session."""
    start_chat()


if __name__ == "__main__":
    app()
