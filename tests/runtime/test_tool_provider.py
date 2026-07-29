from typing import Any

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


def test_populate():
    registry = SkillRegistry()
    registry.register(FakeSkill)

    context = RuntimeContext()

    provider = ToolProvider(registry)

    provider.populate(
        context,
        "hello",
    )

    assert len(context.tools) == 1
    assert context.tools[0].name == "calculator"
