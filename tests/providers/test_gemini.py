import asyncio

from doitall.providers.gemini import GeminiProvider


async def main():
    provider = GeminiProvider()

    response = await provider.chat(
        messages=[
            {
                "role": "user",
                "content": "Reply with only: Doitall Working",
            }
        ]
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())
