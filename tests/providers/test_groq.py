import asyncio

from doitall.providers.groq import GroqProvider


async def main():
    provider = GroqProvider()

    response = await provider.chat(
        messages=[
            {
                "role": "user",
                "content": "Reply with only: Groq Working",
            }
        ]
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())
