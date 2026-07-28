import pytest

from doitall.services.container import ServiceContainer
from doitall.services.tool_executor import ToolExecutor
from doitall.skills.calculator import CalculatorSkill
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry


@pytest.mark.asyncio
async def test_execute_calculator():
    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    executor = ToolExecutor(manager)

    result = await executor.execute(
        "calculator",
        {
            "expression": "2+3*4",
        },
    )

    assert result == 14
