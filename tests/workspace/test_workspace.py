from pathlib import Path

import pytest

from doitall.workspace.workspace import Workspace


def test_workspace_resolve(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    resolved = workspace.resolve("docs/readme.md")

    assert resolved == tmp_path / "docs" / "readme.md"


def test_workspace_mkdir(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    directory = workspace.mkdir("knowledge")

    assert directory.exists()
    assert directory.is_dir()


def test_workspace_exists(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    assert not workspace.exists("memory")

    workspace.mkdir("memory")

    assert workspace.exists("memory")


def test_workspace_prevents_escape(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    with pytest.raises(ValueError):
        workspace.resolve("../outside")


def test_write_and_read_text(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    workspace.write_text(
        "docs/test.txt",
        "Hello Doitall",
    )

    assert workspace.read_text("docs/test.txt") == "Hello Doitall"


def test_delete_file(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    workspace.write_text(
        "temp.txt",
        "Delete me",
    )

    workspace.delete("temp.txt")

    assert not workspace.exists("temp.txt")


def test_list_files(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    workspace.write_text("a.txt", "A")
    workspace.write_text("b.txt", "B")

    files = workspace.list_files()

    assert len(files) == 2


def test_copy_file(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    workspace.write_text(
        "source.txt",
        "Hello",
    )

    workspace.copy(
        "source.txt",
        "copy.txt",
    )

    assert workspace.read_text("copy.txt") == "Hello"


def test_move_file(tmp_path: Path) -> None:
    workspace = Workspace(tmp_path)

    workspace.write_text(
        "source.txt",
        "Hello",
    )

    workspace.move(
        "source.txt",
        "folder/destination.txt",
    )

    assert not workspace.exists("source.txt")

    assert workspace.read_text("folder/destination.txt") == "Hello"
