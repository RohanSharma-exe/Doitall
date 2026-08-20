"""Interactive CLI terminal chat module."""

import asyncio
import sys

from rich.console import Console

from doitall import Doitall

# Rich console instance for formatted terminal outputs
console = Console()


async def run_chat() -> None:
    """Run an interactive streaming chat session loop in the terminal."""
    assistant = Doitall()

    console.print("[bold green]Doitall Chat[/bold green]")
    console.print("Type 'exit' or 'quit' to end the session, or press Ctrl+C.\n")

    while True:
        try:
            prompt = console.input("[bold cyan]You[/bold cyan]: ").strip()
        except (EOFError, KeyboardInterrupt):
            # Terminal closed, pipe broken, or Ctrl+C / Ctrl+Z pressed.
            # Exit cleanly without printing a traceback.
            console.print("\n[dim]Session ended.[/dim]")
            break

        if not prompt:
            continue

        if prompt.lower() in {"exit", "quit"}:
            console.print("[dim]Goodbye![/dim]")
            break

        console.print()
        console.print(
            "[bold green]Assistant[/bold green]: ",
            end="",
        )

        try:
            async for chunk in assistant.stream_chat(prompt):
                sys.stdout.write(chunk)
                sys.stdout.flush()
        except (asyncio.CancelledError, KeyboardInterrupt):
            # User interrupted mid-stream — stop cleanly.
            pass

        print("\n")
