from unittest.mock import AsyncMock

import pytest

from doitall.commands import default_registry
from doitall.commands.executor import SlashCommandExecutor
from doitall.models.provider_response import ProviderResponse
from doitall.providers.base import BaseProvider
from doitall.providers.manager import ProviderManager
from doitall.skills.builtin import register_builtin_skills
from doitall.skills.registry import SkillRegistry


class FakeProvider(BaseProvider):
    def __init__(
        self,
        name: str,
        models: list[str],
        healthy: bool = True,
    ) -> None:
        super().__init__(name)

        self._models = models
        self._healthy = healthy
        self._chat = AsyncMock(return_value=ProviderResponse(content=""))

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> ProviderResponse:
        return await self._chat(messages, **kwargs)

    async def health_check(self) -> bool:
        return self._healthy

    async def available_models(self) -> list[str]:
        return self._models


@pytest.fixture
def command_executor():
    providers = ProviderManager()
    providers.register(FakeProvider("openai", ["gpt-4o"]), default=True)
    providers.register(FakeProvider("anthropic", ["claude-3-5-sonnet"]))

    skills = SkillRegistry()
    register_builtin_skills(skills)

    return SlashCommandExecutor(default_registry(), providers, skills)


@pytest.mark.asyncio
async def test_slash_model_lists_connected_models(command_executor):
    result = await command_executor.execute("/model")

    assert result is not None
    assert "Connected models:" in result.content
    assert "openai (default): gpt-4o" in result.content
    assert "anthropic: claude-3-5-sonnet" in result.content


@pytest.mark.asyncio
async def test_slash_help_lists_commands(command_executor):
    result = await command_executor.execute("/help")

    assert result is not None
    assert "`/model`" in result.content
    assert "`/web-search`" in result.content


@pytest.mark.asyncio
async def test_unknown_command_returns_helpful_message(command_executor):
    result = await command_executor.execute("/missing")

    assert result is not None
    assert "Unknown command `/missing`" in result.content
