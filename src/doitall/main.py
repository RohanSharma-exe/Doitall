"""CLI main entry point runner for Doitall application."""

from doitall.cli import app


def main() -> None:
    """Execute Typer CLI application."""
    app()


if __name__ == "__main__":
    main()
