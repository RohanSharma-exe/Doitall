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


@pytest.mark.asyncio
async def test_rejects_string_literals():
    skill = CalculatorSkill()

    with pytest.raises(ValueError, match="Unsupported expression."):
        await skill.execute(expression='"not a number"')


@pytest.mark.asyncio
async def test_rejects_boolean_literals():
    skill = CalculatorSkill()

    with pytest.raises(ValueError, match="Unsupported expression."):
        await skill.execute(expression="True")


@pytest.mark.asyncio
async def test_rejects_unsupported_operators():
    skill = CalculatorSkill()

    with pytest.raises(ValueError, match="Unsupported expression."):
        await skill.execute(expression="5 // 2")
