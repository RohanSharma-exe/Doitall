import pytest

from doitall.agent.executor import AgentExecutor


class FakeRuntime:
    async def execute(self, context):
        return "ok"


@pytest.mark.asyncio
async def test_agent_executor():
    executor = AgentExecutor(FakeRuntime())

    result = await executor.execute(None)

    assert result == "ok"
