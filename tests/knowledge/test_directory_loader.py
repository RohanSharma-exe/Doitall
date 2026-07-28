from unittest.mock import Mock

from doitall.knowledge.directory_loader import DirectoryLoader
from doitall.knowledge.loader_registry import LoaderRegistry


def test_directory_loader(tmp_path):
    (tmp_path / "a.txt").write_text(
        "One",
        encoding="utf-8",
    )

    (tmp_path / "b.md").write_text(
        "Two",
        encoding="utf-8",
    )

    loader = DirectoryLoader()

    documents = loader.load(str(tmp_path))

    assert len(documents) == 2


def test_directory_loader_ignores_unknown_files(
    tmp_path,
):
    (tmp_path / "a.txt").write_text(
        "One",
        encoding="utf-8",
    )

    (tmp_path / "image.png").write_bytes(b"123")

    loader = DirectoryLoader()

    documents = loader.load(str(tmp_path))

    assert len(documents) == 1
    assert documents[0].content == "One"


def test_custom_registry(tmp_path):
    file = tmp_path / "sample.xyz"

    file.write_text(
        "hello",
        encoding="utf-8",
    )

    loader = Mock()

    loader.load.return_value = []

    registry = LoaderRegistry()

    registry.register(
        ".xyz",
        loader,
    )

    directory_loader = DirectoryLoader(
        registry=registry,
    )

    directory_loader.load(str(tmp_path))

    loader.load.assert_called_once()
