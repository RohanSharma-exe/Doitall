import pytest

from doitall.agent.executor import AgentExecutor
from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall, ToolResult
from doitall.runtime.context import RuntimeContext
from doitall.runtime.tool_message_builder import ToolMessageBuilder


class FakeRuntime:
    def __init__(self):
        self.calls = 0

    async def execute(self, context):
        self.calls += 1

        if self.calls == 1:
            return ProviderResponse(
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="calculator",
                        arguments={
                            "expression": "25*18",
                        },
                    )
                ]
            )

        return ProviderResponse(
            content="450",
        )


class FakeToolEngine:
    async def execute(self, response):
        return [
            ToolResult(
                tool_call_id="1",
                name="calculator",
                result=450,
            )
        ]


@pytest.mark.asyncio
async def test_agent_executes_tool_loop():
    runtime = FakeRuntime()

    executor = AgentExecutor(
        runtime,
        FakeToolEngine(),
        ToolMessageBuilder(),
    )

    context = RuntimeContext()

    response = await executor.execute(context)

    assert response.content == "450"

    assert runtime.calls == 2

    assert len(context.messages) == 1
    assert context.messages[0].content == "450"
