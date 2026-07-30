from typing import Any

import pytest

from doitall.models.tool_definition import ToolDefinition
from doitall.runtime.context import RuntimeContext
from doitall.runtime.tool_provider import ToolProvider
from doitall.skills.base import BaseSkill
from doitall.skills.registry import SkillRegistry


class FakeSkill(BaseSkill):
    name = "calculator"
    description = "Calculator"

    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.name,
            description=cls.description,
        )

    async def execute(self, **kwargs: Any) -> Any:
        return 42


@pytest.mark.asyncio
async def test_populate():
    registry = SkillRegistry()
    registry.register(FakeSkill)

    context = RuntimeContext()

    provider = ToolProvider(registry)

    await provider.populate(context)

    assert len(context.tools) == 1
    assert context.tools[0].name == "calculator"
