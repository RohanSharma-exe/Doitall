import pytest

from doitall.agent.executor import AgentExecutor
from doitall.config.settings import settings
from doitall.models.message import AssistantMessage, ToolMessage
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

    assert len(context.messages) == 2

    assistant = context.messages[0]
    tool = context.messages[1]

    assert isinstance(assistant, AssistantMessage)
    assert assistant.content == ""
    assert len(assistant.tool_calls) == 1

    assert isinstance(tool, ToolMessage)
    assert tool.content == "450"
    assert tool.tool_call_id == assistant.tool_calls[0].id

    assert response.content == "450"


@pytest.mark.asyncio
async def test_agent_stops_after_max_tool_iterations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test agent stops after MAX_TOOL_ITERATIONS is reached."""
    monkeypatch.setattr(settings, "MAX_TOOL_ITERATIONS", 3)

    class InfiniteToolRuntime:
        def __init__(self) -> None:
            self.calls = 0

        async def execute(self, context: RuntimeContext) -> ProviderResponse:
            self.calls += 1

            return ProviderResponse(
                tool_calls=[
                    ToolCall(
                        id=f"call-{self.calls}",
                        name="calculator",
                        arguments={"expression": "1+1"},
                    )
                ]
            )

    class CountingToolEngine:
        def __init__(self) -> None:
            self.calls = 0

        async def execute(
            self,
            response: ProviderResponse,
        ) -> list[ToolResult]:
            self.calls += 1

            return [
                ToolResult(
                    tool_call_id=response.tool_calls[0].id,
                    name="calculator",
                    result=2,
                )
            ]

    runtime = InfiniteToolRuntime()
    tool_engine = CountingToolEngine()

    executor = AgentExecutor(
        runtime,
        tool_engine,
        ToolMessageBuilder(),
    )

    context = RuntimeContext()

    response = await executor.execute(context)

    assert response.tool_calls
    assert runtime.calls == settings.MAX_TOOL_ITERATIONS + 1
    assert tool_engine.calls == settings.MAX_TOOL_ITERATIONS


@pytest.mark.asyncio
async def test_agent_stops_when_tool_call_budget_is_exceeded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test agent refuses to execute tools beyond the request budget."""
    monkeypatch.setattr(settings, "MAX_TOOL_CALLS_PER_REQUEST", 2)

    class BudgetRuntime:
        def __init__(self) -> None:
            self.calls = 0

        async def execute(self, context: RuntimeContext) -> ProviderResponse:
            self.calls += 1

            return ProviderResponse(
                tool_calls=[
                    ToolCall(
                        id=f"call-{self.calls}-1",
                        name="calculator",
                        arguments={"expression": "1+1"},
                    ),
                    ToolCall(
                        id=f"call-{self.calls}-2",
                        name="calculator",
                        arguments={"expression": "2+2"},
                    ),
                    ToolCall(
                        id=f"call-{self.calls}-3",
                        name="calculator",
                        arguments={"expression": "3+3"},
                    ),
                ]
            )

    class CountingToolEngine:
        def __init__(self) -> None:
            self.calls = 0

        async def execute(
            self,
            response: ProviderResponse,
        ) -> list[ToolResult]:
            self.calls += 1
            return [
                ToolResult(
                    tool_call_id=call.id,
                    name=call.name,
                    result=2,
                )
                for call in response.tool_calls
            ]

    runtime = BudgetRuntime()
    tool_engine = CountingToolEngine()

    executor = AgentExecutor(
        runtime,
        tool_engine,
        ToolMessageBuilder(),
    )

    context = RuntimeContext()

    response = await executor.execute(context)

    assert response.tool_calls
    assert runtime.calls == 1
    assert tool_engine.calls == 0
    assert context.messages == []


@pytest.mark.asyncio
async def test_agent_stops_after_repeated_identical_tool_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test agent stops when the same tool call is repeatedly requested."""
    monkeypatch.setattr(settings, "MAX_IDENTICAL_TOOL_CALLS", 2)

    class RepeatingToolRuntime:
        def __init__(self) -> None:
            self.calls = 0

        async def execute(self, context: RuntimeContext) -> ProviderResponse:
            self.calls += 1

            return ProviderResponse(
                tool_calls=[
                    ToolCall(
                        id=f"call-{self.calls}",
                        name="calculator",
                        arguments={"expression": "2+2"},
                    )
                ]
            )

    class CountingToolEngine:
        def __init__(self) -> None:
            self.calls = 0

        async def execute(
            self,
            response: ProviderResponse,
        ) -> list[ToolResult]:
            self.calls += 1

            return [
                ToolResult(
                    tool_call_id=response.tool_calls[0].id,
                    name=response.tool_calls[0].name,
                    result=4,
                )
            ]

    runtime = RepeatingToolRuntime()
    tool_engine = CountingToolEngine()

    executor = AgentExecutor(
        runtime,
        tool_engine,
        ToolMessageBuilder(),
    )

    context = RuntimeContext()

    response = await executor.execute(context)

    assert response.tool_calls
    assert runtime.calls == 3
    assert tool_engine.calls == 2


def test_tool_call_signature_is_stable_for_argument_order() -> None:
    executor = AgentExecutor(
        runtime=None,  # type: ignore[arg-type]
        tool_engine=None,  # type: ignore[arg-type]
        tool_message_builder=None,  # type: ignore[arg-type]
    )

    first = ToolCall(
        name="calculator",
        arguments={
            "expression": "2+2",
            "precision": 2,
        },
    )

    second = ToolCall(
        name="calculator",
        arguments={
            "precision": 2,
            "expression": "2+2",
        },
    )

    assert executor._tool_call_signature(first) == executor._tool_call_signature(second)


@pytest.mark.asyncio
async def test_agent_feeds_tool_failure_back_to_runtime() -> None:
    class FailureRuntime:
        def __init__(self) -> None:
            self.calls = 0
            self.contexts: list[RuntimeContext] = []

        async def execute(
            self,
            context: RuntimeContext,
        ) -> ProviderResponse:
            self.calls += 1
            self.contexts.append(context)

            if self.calls == 1:
                return ProviderResponse(
                    tool_calls=[
                        ToolCall(
                            id="failed-call",
                            name="calculator",
                            arguments={"expression": "invalid"},
                        )
                    ]
                )

            return ProviderResponse(content="I couldn't execute that calculation.")

    class FailureToolEngine:
        async def execute(
            self,
            response: ProviderResponse,
        ) -> list[ToolResult]:
            return [
                ToolResult(
                    tool_call_id="failed-call",
                    name="calculator",
                    result="Tool execution failed: invalid expression",
                )
            ]

    runtime = FailureRuntime()

    executor = AgentExecutor(
        runtime,
        FailureToolEngine(),
        ToolMessageBuilder(),
    )

    context = RuntimeContext()

    response = await executor.execute(context)

    assert response.content == "I couldn't execute that calculation."
    assert runtime.calls == 2

    assert len(context.messages) == 2

    assistant = context.messages[0]
    tool = context.messages[1]

    assert isinstance(assistant, AssistantMessage)
    assert len(assistant.tool_calls) == 1
    assert assistant.tool_calls[0].id == "failed-call"

    assert isinstance(tool, ToolMessage)
    assert tool.tool_call_id == "failed-call"
    assert tool.name == "calculator"
    assert tool.content == "Tool execution failed: invalid expression"
