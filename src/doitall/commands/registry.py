"""Modular slash command registry for assistant commands."""

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel, Field

CommandCategory = Literal["core", "development", "workspace", "ai"]


class Command(BaseModel):
    """Public command metadata discoverable by clients and plugins."""

    name: str
    category: CommandCategory
    description: str
    icon: str = "terminal"
    aliases: list[str] = Field(default_factory=list)
    arguments: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    hidden: bool = False
    localization_key: str | None = None


class CommandRegistry:
    """In-memory command registry with alias-aware lookup."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._aliases: dict[str, str] = {}

    def register(self, command: Command) -> None:
        key = self._normalize(command.name)
        if key in self._commands:
            raise ValueError(f"Command already registered: {command.name}")
        self._commands[key] = command
        for alias in command.aliases:
            alias_key = self._normalize(alias)
            if alias_key in self._aliases or alias_key in self._commands:
                raise ValueError(f"Command alias already registered: {alias}")
            self._aliases[alias_key] = key

    def register_many(self, commands: Iterable[Command]) -> None:
        for command in commands:
            self.register(command)

    def get(self, name_or_alias: str) -> Command:
        key = self._normalize(name_or_alias)
        key = self._aliases.get(key, key)
        return self._commands[key]

    def list(self, *, include_hidden: bool = False) -> list[Command]:
        commands = list(self._commands.values())
        if not include_hidden:
            commands = [command for command in commands if not command.hidden]
        return sorted(commands, key=lambda command: (command.category, command.name))

    def clear(self) -> None:
        self._commands.clear()
        self._aliases.clear()

    @staticmethod
    def _normalize(value: str) -> str:
        value = value.strip().lower()
        return value if value.startswith("/") else f"/{value}"


def _builtin_commands() -> list[Command]:
    data: list[tuple[CommandCategory, list[str]]] = [
        ("core", ["models", "providers", "skills", "tools", "agents", "memory", "settings", "help", "clear", "new", "history", "search", "export", "import"]),
        ("development", ["system", "logs", "doctor", "health", "config", "version"]),
        ("workspace", ["files", "projects", "workspace", "index", "sync"]),
        ("ai", ["reasoning", "thinking", "context", "prompts", "templates", "mcp", "rag", "knowledge"]),
    ]
    descriptions = {
        "help": "Show available commands and shortcuts.",
        "clear": "Clear the current conversation view.",
        "new": "Start a new chat session.",
        "thinking": "Toggle the safe thinking timeline.",
        "providers": "Show configured AI providers.",
        "models": "Show available AI models.",
    }
    commands: list[Command] = []
    for category, names in data:
        for name in names:
            commands.append(
                Command(
                    name=f"/{name}",
                    category=category,
                    description=descriptions.get(name, f"Open {name} controls."),
                    icon="sparkles" if category == "ai" else "terminal",
                    localization_key=f"commands.{name}",
                )
            )
    return commands


def default_registry() -> CommandRegistry:
    registry = CommandRegistry()
    registry.register_many(_builtin_commands())
    return registry
