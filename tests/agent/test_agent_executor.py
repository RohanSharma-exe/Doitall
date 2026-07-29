import pytest

from doitall.agent.executor import AgentExecutor
from doitall.models.provider_response import ProviderResponse
from doitall.runtime.context import RuntimeContext
from doitall.runtime.tool_message_builder import ToolMessageBuilder


class FakeRuntime:
    def __init__(self):
        self.calls = 0

    async def execute(self, context):
        self.calls += 1

        return ProviderResponse(
            content="Done",
        )


class FakeToolEngine:
    async def execute(self, response):
        return []


@pytest.mark.asyncio
async def test_agent_executor_without_tool_calls():
    runtime = FakeRuntime()

    executor = AgentExecutor(
        runtime,
        FakeToolEngine(),
        ToolMessageBuilder(),
    )

    response = await executor.execute(
        RuntimeContext(),
    )

    assert response.content == "Done"
    assert runtime.calls == 1
