import asyncio

from doitall.application import Doitall


async def main():
    print("=== Session 1 ===")

    app = Doitall()

    response = await app.chat("My favourite language is Python.")
    print(response)

    print("\nRestarting...\n")

    print("=== Session 2 ===")

    app = Doitall()

    response = await app.chat("What is my favourite language?")
    print(response)


asyncio.run(main())
