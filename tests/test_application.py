"""Top-level package import verification test."""

from doitall import Doitall


def test_import() -> None:
    """Verify Doitall application class can be imported from package root."""
    assert Doitall is not None
