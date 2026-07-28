from doitall.skills.base import BaseSkill


class EchoSkill(BaseSkill):
    name = "echo"
    description = "Echo skill"

    async def execute(self, **kwargs):
        return kwargs


def test_defaults():
    skill = EchoSkill()

    assert skill.name == "echo"
    assert skill.description == "Echo skill"
    assert skill.version == "1.0.0"
    assert skill.enabled is True
