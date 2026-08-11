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
