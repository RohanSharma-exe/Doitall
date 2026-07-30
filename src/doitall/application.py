from doitall.agent.agent import Agent
from doitall.core.bootstrap import bootstrap, cleanup
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
        self._is_running = False

    async def chat(
        self,
        message: str,
    ) -> str:
        return await self._chat_service.chat(message)

    def start(self) -> None:
        """Start the application."""
        if self._is_running:
            return

        self._is_running = True

    def stop(self) -> None:
        """Stop the application and clean up resources."""
        if not self._is_running:
            return

        self._is_running = False
        cleanup()

    @property
    def is_running(self) -> bool:
        """Check if the application is running."""
        return self._is_running
