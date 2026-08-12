import asyncio

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall
from doitall.services.container import ServiceContainer
from doitall.services.tool_calling_engine import ToolCallingEngine
from doitall.services.tool_executor import ToolExecutor
from doitall.skills.calculator import CalculatorSkill
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry


@pytest.mark.asyncio
async def test_execute_tool_calls():
    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    executor = ToolExecutor(manager)
    engine = ToolCallingEngine(executor)

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="1",
                name="calculator",
                arguments={
                    "expression": "2+3",
                },
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 1
    assert results[0].tool_call_id == "1"
    assert results[0].result == 5


@pytest.mark.asyncio
async def test_execute_multiple_tool_calls():
    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    executor = ToolExecutor(manager)
    engine = ToolCallingEngine(executor)

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="1",
                name="calculator",
                arguments={
                    "expression": "2+2",
                },
            ),
            ToolCall(
                id="2",
                name="calculator",
                arguments={
                    "expression": "10*5",
                },
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 2
    assert results[0].result == 4
    assert results[1].result == 50


@pytest.mark.asyncio
async def test_execute_tool_calls_continues_after_failure() -> None:
    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    executor = ToolExecutor(manager)
    engine = ToolCallingEngine(executor)

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="failed",
                name="unknown_skill",
                arguments={},
            ),
            ToolCall(
                id="successful",
                name="calculator",
                arguments={
                    "expression": "10*5",
                },
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 2

    assert results[0].tool_call_id == "failed"
    assert results[0].name == "unknown_skill"
    assert isinstance(results[0].result, str)
    assert results[0].result.startswith("Tool execution failed:")

    assert results[1].tool_call_id == "successful"
    assert results[1].name == "calculator"
    assert results[1].result == 50


@pytest.mark.asyncio
async def test_execute_tool_call_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    executor = ToolExecutor(manager)
    engine = ToolCallingEngine(executor)

    async def slow_execute(
        name: str,
        arguments: dict[str, object],
    ) -> object:
        await asyncio.sleep(1)
        return "should not complete"

    monkeypatch.setattr(
        executor,
        "execute",
        slow_execute,
    )

    monkeypatch.setattr(
        "doitall.services.tool_calling_engine.settings.TOOL_EXECUTION_TIMEOUT_SECONDS",
        0.01,
    )

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="timeout",
                name="slow_tool",
                arguments={},
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 1
    assert results[0].tool_call_id == "timeout"
    assert results[0].name == "slow_tool"
    assert results[0].result == "Tool execution timed out after 0.01 seconds."


@pytest.mark.asyncio
async def test_timeout_does_not_prevent_remaining_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    executor = ToolExecutor(manager)
    engine = ToolCallingEngine(executor)

    monkeypatch.setattr(
        "doitall.services.tool_calling_engine.settings.TOOL_EXECUTION_TIMEOUT_SECONDS",
        0.01,
    )

    original_execute = executor.execute

    async def execute_with_one_timeout(
        name: str,
        arguments: dict[str, object],
    ) -> object:
        if name == "slow_tool":
            await asyncio.sleep(1)

        return await original_execute(name, arguments)

    executor.execute = execute_with_one_timeout  # type: ignore[method-assign]

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="timeout",
                name="slow_tool",
                arguments={},
            ),
            ToolCall(
                id="successful",
                name="calculator",
                arguments={
                    "expression": "10*5",
                },
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 2

    assert results[0].tool_call_id == "timeout"
    assert results[0].result.startswith("Tool execution timed out")

    assert results[1].tool_call_id == "successful"
    assert results[1].result == 50


@pytest.mark.asyncio
async def test_execute_tool_calls_concurrently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    executor = ToolExecutor(manager)
    engine = ToolCallingEngine(executor)

    active_calls = 0
    max_active_calls = 0

    original_execute = executor.execute

    async def tracked_execute(
        name: str,
        arguments: dict[str, object],
    ) -> object:
        nonlocal active_calls, max_active_calls

        active_calls += 1
        max_active_calls = max(max_active_calls, active_calls)

        try:
            await asyncio.sleep(0.05)
            return await original_execute(name, arguments)
        finally:
            active_calls -= 1

    monkeypatch.setattr(
        executor,
        "execute",
        tracked_execute,
    )

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="1",
                name="calculator",
                arguments={"expression": "2+3"},
            ),
            ToolCall(
                id="2",
                name="calculator",
                arguments={"expression": "10*5"},
            ),
            ToolCall(
                id="3",
                name="calculator",
                arguments={"expression": "7*6"},
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 3
    assert max_active_calls == 3

    assert results[0].tool_call_id == "1"
    assert results[0].result == 5

    assert results[1].tool_call_id == "2"
    assert results[1].result == 50

    assert results[2].tool_call_id == "3"
    assert results[2].result == 42
