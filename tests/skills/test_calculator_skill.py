import pytest

from doitall.skills.calculator import CalculatorSkill


@pytest.mark.asyncio
async def test_addition():
    skill = CalculatorSkill()

    result = await skill.execute(expression="2 + 3")

    assert result == 5


@pytest.mark.asyncio
async def test_operator_precedence():
    skill = CalculatorSkill()

    result = await skill.execute(expression="2 + 3 * 4")

    assert result == 14


@pytest.mark.asyncio
async def test_parentheses():
    skill = CalculatorSkill()

    result = await skill.execute(expression="(2 + 3) * 4")

    assert result == 20
