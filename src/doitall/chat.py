import asyncio

from rich import print

from doitall import Doitall


async def run_chat() -> None:
    assistant = Doitall()

    print("[bold green]🚀 Doitall Chat[/bold green]")
    print("Type 'exit' to quit.\n")

    while True:
        prompt = input("You: ").strip()

        if prompt.lower() in {"exit", "quit"}:
            break

        response = await assistant.chat(prompt)

        print(f"\nAssistant: {response}\n")


def start_chat() -> None:
    asyncio.run(run_chat())
