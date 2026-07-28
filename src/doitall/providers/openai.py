from typing import Any

from doitall.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__("openai")

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError

    async def embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True
