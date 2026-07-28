from doitall.agent.agent import Agent
from doitall.agent.manager import AgentManager


def test_agent_manager():
    manager = AgentManager(
        Agent(
            name="Assistant",
            system_prompt="You help users.",
        )
    )

    assert manager.name == "Assistant"
    assert manager.system_prompt == "You help users."
