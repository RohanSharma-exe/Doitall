from pathlib import Path

import pytest

from doitall.skills.filesystem import FilesystemSkill
from doitall.workspace.workspace import Workspace


@pytest.fixture
def skill(tmp_path: Path) -> FilesystemSkill:
    workspace = Workspace(tmp_path)
    return FilesystemSkill(workspace)


@pytest.mark.asyncio
async def test_write_and_read(skill: FilesystemSkill):
    await skill.execute(
        action="write",
        path="hello.txt",
        content="Hello",
    )

    result = await skill.execute(
        action="read",
        path="hello.txt",
    )

    assert result == "Hello"


@pytest.mark.asyncio
async def test_exists(skill: FilesystemSkill):
    await skill.execute(
        action="write",
        path="file.txt",
        content="data",
    )

    assert await skill.execute(
        action="exists",
        path="file.txt",
    )


@pytest.mark.asyncio
async def test_list(skill: FilesystemSkill):
    await skill.execute(
        action="write",
        path="a.txt",
        content="A",
    )

    await skill.execute(
        action="write",
        path="b.txt",
        content="B",
    )

    files = await skill.execute(
        action="list",
    )

    assert sorted(files) == [
        "a.txt",
        "b.txt",
    ]


@pytest.mark.asyncio
async def test_delete(skill: FilesystemSkill):
    await skill.execute(
        action="write",
        path="delete.txt",
        content="Delete",
    )

    await skill.execute(
        action="delete",
        path="delete.txt",
    )

    assert not await skill.execute(
        action="exists",
        path="delete.txt",
    )


@pytest.mark.asyncio
async def test_unknown_action(skill: FilesystemSkill):
    with pytest.raises(ValueError):
        await skill.execute(action="invalid")
