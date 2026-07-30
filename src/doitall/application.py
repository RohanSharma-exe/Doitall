from doitall.agent.agent import Agent
from doitall.core.bootstrap import bootstrap
from doitall.runtime.runtime_factory import RuntimeFactory


class Doitall:
    """Public entry point for the Doitall framework."""

    def __init__(self) -> None:
        bootstrap()

        factory = RuntimeFactory()

        agent = Agent(
            name="Doitall",
            system_prompt="You are a helpful AI assistant.",
        )

        self._chat_service = factory.create(agent)

    async def chat(
        self,
        message: str,
    ) -> str:
        return await self._chat_service.chat(message)

    def start(self) -> None:
        """Start the application."""

    def stop(self) -> None:
        """Stop the application."""
