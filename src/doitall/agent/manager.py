"""Agent metadata manager and wrapper module."""

from doitall.agent.agent import Agent


class AgentManager:
    """Provides property accessors for agent metadata and prompt configuration."""

    def __init__(
        self,
        agent: Agent,
    ) -> None:
        """Initialize AgentManager with target Agent instance."""
        self.agent = agent

    @property
    def system_prompt(self) -> str:
        """Return agent system prompt string."""
        return self.agent.system_prompt

    @property
    def name(self) -> str:
        """Return agent name string."""
        return self.agent.name
