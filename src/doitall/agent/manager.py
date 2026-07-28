from doitall.agent.agent import Agent


class AgentManager:
    def __init__(
        self,
        agent: Agent,
    ) -> None:
        self.agent = agent

    @property
    def system_prompt(self) -> str:
        return self.agent.system_prompt

    @property
    def name(self) -> str:
        return self.agent.name
