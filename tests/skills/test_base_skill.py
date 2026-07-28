import pytest

from doitall.skills.base import BaseSkill


class EchoSkill(BaseSkill):
    name = "echo"
    description = "Echoes text."

    async def execute(self, **kwargs):
        return kwargs["text"]


@pytest.mark.asyncio
async def test_base_skill_execute():
    skill = EchoSkill()

    result = await skill.execute(text="Hello")

    assert result == "Hello"
