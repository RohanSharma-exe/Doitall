import pytest

from doitall.core.exceptions import SkillError
from doitall.services.container import ServiceContainer
from doitall.skills.base import BaseSkill
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry


class EchoSkill(BaseSkill):
    name = "echo"
    description = "Echo"

    async def execute(self, **kwargs):
        return kwargs["text"]


@pytest.mark.asyncio
async def test_execute_registered_skill():
    registry = SkillRegistry()

    registry.register(EchoSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    result = await manager.execute(
        "echo",
        text="Hello",
    )

    assert result == "Hello"


@pytest.mark.asyncio
async def test_unknown_skill_raises_skill_error():
    registry = SkillRegistry()

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    with pytest.raises(SkillError):
        await manager.execute("missing")


class DisabledSkill(BaseSkill):
    name = "disabled"
    enabled = False

    async def execute(self, **kwargs):
        return "never"


@pytest.mark.asyncio
async def test_disabled_skill_raises():
    registry = SkillRegistry()
    registry.register(DisabledSkill)

    container = ServiceContainer()
    manager = SkillManager(
        registry,
        container,
    )

    with pytest.raises(ValueError):
        await manager.execute("disabled")


class Dependency:
    def hello(self) -> str:
        return "world"


class DependencySkill(BaseSkill):
    name = "dependency"

    def __init__(
        self,
        dependency: Dependency,
    ) -> None:
        self._dependency = dependency

    async def execute(self, **kwargs):
        return self._dependency.hello()


@pytest.mark.asyncio
async def test_constructor_dependency_injection():
    registry = SkillRegistry()
    registry.register(DependencySkill)

    container = ServiceContainer()
    container.register(
        "dependency",
        Dependency(),
    )

    manager = SkillManager(
        registry,
        container,
    )

    result = await manager.execute("dependency")

    assert result == "world"


@pytest.mark.asyncio
async def test_invalid_arguments_raise_skill_error() -> None:
    """Reject arguments that do not match the skill input schema."""
    from doitall.skills.calculator import CalculatorSkill

    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    with pytest.raises(SkillError, match="Invalid arguments"):
        await manager.execute(
            "calculator",
            expression=123,
        )


@pytest.mark.asyncio
async def test_missing_required_argument_raises_skill_error() -> None:
    """Reject tool calls missing required arguments."""
    from doitall.skills.calculator import CalculatorSkill

    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    with pytest.raises(SkillError, match="Invalid arguments"):
        await manager.execute(
            "calculator",
        )


@pytest.mark.asyncio
async def test_unknown_argument_raises_skill_error() -> None:
    """Reject arguments not declared by the skill schema."""
    from doitall.skills.calculator import CalculatorSkill

    registry = SkillRegistry()
    registry.register(CalculatorSkill)

    container = ServiceContainer()

    manager = SkillManager(
        registry,
        container,
    )

    with pytest.raises(SkillError, match="Invalid arguments"):
        await manager.execute(
            "calculator",
            expression="2+3",
            unexpected="value",
        )
