from pathlib import Path

import pytest

from doitall.skills.filesystem import FilesystemSkill
from doitall.workspace.workspace import Workspace


@pytest.fixture
def skill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FilesystemSkill:
    monkeypatch.setattr(
        "doitall.skills.filesystem.settings.ENABLE_FILESYSTEM_WRITE_TOOLS",
        True,
    )
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


@pytest.mark.asyncio
async def test_write_denied_by_default(tmp_path: Path):
    skill = FilesystemSkill(Workspace(tmp_path))

    with pytest.raises(PermissionError):
        await skill.execute(
            action="write",
            path="hello.txt",
            content="Hello",
        )


@pytest.mark.asyncio
async def test_read_denies_secret_files(tmp_path: Path):
    (tmp_path / ".env").write_text("SECRET=value")
    skill = FilesystemSkill(Workspace(tmp_path))

    with pytest.raises(PermissionError):
        await skill.execute(action="read", path=".env")


@pytest.mark.asyncio
async def test_read_denies_oversized_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        "doitall.skills.filesystem.settings.FILESYSTEM_MAX_READ_BYTES", 3
    )
    (tmp_path / "large.txt").write_text("large")
    skill = FilesystemSkill(Workspace(tmp_path))

    with pytest.raises(PermissionError):
        await skill.execute(action="read", path="large.txt")
