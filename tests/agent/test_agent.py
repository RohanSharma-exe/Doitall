from doitall.agent.agent import Agent


def test_agent():
    agent = Agent(
        name="Assistant",
    )

    assert agent.name == "Assistant"
