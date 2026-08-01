import pytest

from doitall.commands import Command, CommandRegistry, default_registry


def test_default_registry_contains_required_commands():
    registry = default_registry()
    names = {command.name for command in registry.list()}

    for name in [
        "/model",
        "/models",
        "/providers",
        "/skills",
        "/tools",
        "/thinking",
        "/knowledge",
        "/web-search",
        "/web-fetch",
    ]:
        assert name in names


def test_registry_resolves_aliases():
    registry = CommandRegistry()
    registry.register(
        Command(
            name="/settings",
            category="core",
            description="Settings",
            aliases=["prefs"],
        )
    )

    assert registry.get("prefs").name == "/settings"
    assert registry.get("/prefs").name == "/settings"


def test_hidden_commands_are_excluded_by_default():
    registry = CommandRegistry()
    registry.register(
        Command(
            name="/internal",
            category="development",
            description="Internal",
            hidden=True,
        )
    )

    assert registry.list() == []
    assert registry.list(include_hidden=True)[0].name == "/internal"


def test_duplicate_aliases_are_rejected():
    registry = CommandRegistry()
    registry.register(
        Command(name="/one", category="core", description="One", aliases=["x"])
    )

    with pytest.raises(ValueError):
        registry.register(
            Command(name="/two", category="core", description="Two", aliases=["x"])
        )
