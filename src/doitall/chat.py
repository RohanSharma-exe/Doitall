"""Interactive CLI terminal chat module."""

import sys

from rich.console import Console

from doitall import Doitall

# Rich console instance for formatted terminal outputs
console = Console()


async def run_chat() -> None:
    """Run an interactive streaming chat session loop in the terminal."""
    assistant = Doitall()

    console.print("[bold green]Doitall Chat[/bold green]")
    console.print("Type 'exit' to quit.\n")

    while True:
        prompt = console.input("[bold cyan]You[/bold cyan]: ").strip()

        if prompt.lower() in {"exit", "quit"}:
            break

        console.print()

        console.print(
            "[bold green]Assistant[/bold green]: ",
            end="",
        )

        async for chunk in assistant.stream_chat(prompt):
            sys.stdout.write(chunk)
            sys.stdout.flush()

        print("\n")
