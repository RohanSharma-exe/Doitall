from unittest.mock import Mock

from doitall.knowledge.loader_registry import LoaderRegistry


def test_register():
    registry = LoaderRegistry()

    loader = Mock()

    registry.register(
        ".txt",
        loader,
    )

    assert registry.get(".txt") is loader


def test_unknown_extension():
    registry = LoaderRegistry()

    assert registry.get(".pdf") is None


def test_case_insensitive():
    registry = LoaderRegistry()

    loader = Mock()

    registry.register(
        ".TXT",
        loader,
    )

    assert registry.get(".txt") is loader
    assert registry.get(".TXT") is loader
