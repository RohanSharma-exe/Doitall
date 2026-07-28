import pytest

from doitall.services.container import ServiceContainer
from doitall.skills.base import BaseSkill
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry


class Database:
    pass


def test_register_by_name():
    container = ServiceContainer()

    database = Database()

    container.register(
        "database",
        database,
    )

    assert container.resolve("database") is database


def test_register_by_type():
    container = ServiceContainer()

    database = Database()

    container.register(
        "database",
        database,
    )

    assert container.resolve_type(Database) is database


def test_unknown_type():
    container = ServiceContainer()

    with pytest.raises(KeyError):
        container.resolve_type(Database)


def test_remove_service():
    container = ServiceContainer()

    database = Database()

    container.register(
        "database",
        database,
    )

    container.remove("database")

    assert not container.has("database")
    assert not container.has_type(Database)


class Workspace:
    pass


class TypedSkill(BaseSkill):
    name = "typed"

    def __init__(
        self,
        workspace: Workspace,
    ) -> None:
        self.workspace = workspace

    async def execute(self, **kwargs):
        return self.workspace


@pytest.mark.asyncio
async def test_type_based_dependency_injection():
    registry = SkillRegistry()

    registry.register(TypedSkill)

    container = ServiceContainer()

    workspace = Workspace()

    container.register(
        "workspace",
        workspace,
    )

    manager = SkillManager(
        registry,
        container,
    )

    result = await manager.execute("typed")

    assert result is workspace
