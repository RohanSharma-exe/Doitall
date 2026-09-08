"""Main application facade module for Doitall agent framework."""

from collections.abc import AsyncIterator

from doitall.agent.agent import Agent
from doitall.commands import default_registry
from doitall.commands.executor import SlashCommandExecutor
from doitall.core.bootstrap import bootstrap, cleanup
from doitall.providers.manager import ProviderManager
from doitall.runtime.runtime_factory import RuntimeFactory
from doitall.services.registry import container
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry


class Doitall:
    """Public entry point for the Doitall framework."""

    def __init__(self) -> None:
        """Bootstrap dependencies, initialize runtime services and command executor."""
        bootstrap()

        factory = RuntimeFactory()

        agent = Agent(
            name="Doitall",
            system_prompt="You are a helpful AI assistant.",
        )

        self._chat_service = factory.create(agent)
        provider_manager: ProviderManager = container.resolve("provider_manager")
        skill_registry: SkillRegistry = container.resolve("skill_registry")
        skill_manager: SkillManager = container.resolve("skill_manager")

        self._command_executor = SlashCommandExecutor(
            default_registry(),
            provider_manager,
            skill_registry,
            skill_manager,
            self._chat_service._conversation_service,
        )

    async def stream_chat(
        self,
        message: str,
    ) -> AsyncIterator[str]:
        """Stream response tokens for user prompt or execute slash command if prefixed."""
        if self._command_executor.is_command(message):
            result = await self._command_executor.execute(message)

            if result is not None:
                yield result.content
                return

        async for chunk in self._chat_service.stream_chat(message):
            yield chunk

    async def chat(
        self,
        message: str,
    ) -> str:
        """Send chat completion message or execute slash command synchronously."""
        if self._command_executor.is_command(message):
            result = await self._command_executor.execute(message)

            if result is not None:
                return result.content

        return await self._chat_service.chat(message)

    async def stop(self) -> None:
        """Stop the application and clean up resources."""
        await cleanup()
