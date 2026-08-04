"""Factory for constructing default AI Agent instance."""

from doitall.agent.agent import Agent


def create_default_agent() -> Agent:
    """Instantiate and return the default 'Doitall' AI assistant Agent."""
    return Agent(
        name="Doitall",
        description="Default AI assistant",
        system_prompt="You are Doitall, a helpful AI assistant.",
    )
