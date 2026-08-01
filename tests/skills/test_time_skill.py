import pytest

from doitall.skills.time import TimeSkill


@pytest.mark.asyncio
async def test_time_skill_returns_timezone_and_iso_timestamp():
    result = await TimeSkill().execute(timezone="UTC")

    assert result["timezone"] == "UTC"
    assert result["iso"].endswith("+00:00")
    assert result["utc"].endswith("+00:00")


@pytest.mark.asyncio
async def test_time_skill_rejects_unknown_timezone():
    with pytest.raises(ValueError, match="Unknown timezone"):
        await TimeSkill().execute(timezone="Not/A_Real_Zone")
