from doitall.skills.base import BaseSkill
from doitall.skills.registry import SkillRegistry


class EchoSkill(BaseSkill):
    name = "echo"
    description = "Echo"

    async def execute(self, **kwargs):
        return kwargs


def test_names():
    registry = SkillRegistry()

    registry.register(EchoSkill)

    assert registry.names() == ["echo"]


def test_register_skill():
    registry = SkillRegistry()

    skill = EchoSkill

    registry.register(skill)

    assert registry.exists("echo")
    assert registry.get("echo") is skill


def test_unregister_skill():
    registry = SkillRegistry()

    registry.register(EchoSkill)

    registry.unregister("echo")

    assert not registry.exists("echo")


def test_clear_registry():
    registry = SkillRegistry()

    registry.register(EchoSkill)

    registry.clear()

    assert registry.all() == []


def test_all_returns_registered_skills():
    registry = SkillRegistry()

    registry.register(EchoSkill)

    skills = registry.all()

    assert len(skills) == 1
    assert skills[0].name == "echo"
