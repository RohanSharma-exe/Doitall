"""Execution helpers for slash commands submitted through chat."""

from dataclasses import dataclass
from shlex import split

from doitall.commands import CommandRegistry
from doitall.providers.manager import ProviderManager
from doitall.skills.registry import SkillRegistry


@dataclass(frozen=True)
class CommandResult:
    """Result returned when a slash command is handled locally."""

    content: str


class SlashCommandExecutor:
    """Handles lightweight ChatGPT/Claude-style slash commands in chat input."""

    def __init__(
        self,
        registry: CommandRegistry,
        provider_manager: ProviderManager,
        skill_registry: SkillRegistry,
    ) -> None:
        self._registry = registry
        self._provider_manager = provider_manager
        self._skill_registry = skill_registry

    def is_command(self, content: str) -> bool:
        return content.strip().startswith("/")

    async def execute(self, content: str) -> CommandResult | None:
        parts = split(content.strip())
        if not parts:
            return None

        name = parts[0]
        try:
            command = self._registry.get(name)
        except KeyError:
            return CommandResult(
                content=f"Unknown command `{name}`. Try `/help` to see available commands."
            )

        command_name = command.name
        if command_name == "/help":
            return CommandResult(self._help())
        if command_name in {"/model", "/models"}:
            return CommandResult(await self._models())
        if command_name == "/providers":
            return CommandResult(await self._providers())
        if command_name in {"/tools", "/toolbox", "/skills"}:
            return CommandResult(self._tools())

        return CommandResult(
            content=(
                f"`{command.name}` is available in the command palette, but does not "
                "need a local chat action yet."
            )
        )

    def _help(self) -> str:
        commands = self._registry.list()
        lines = ["Available commands:"]
        for command in commands:
            lines.append(f"- `{command.name}` — {command.description}")
        return "\n".join(lines)

    async def _models(self) -> str:
        lines = ["Connected models:"]
        for candidate in self._provider_manager.fallback_candidates():
            provider = candidate.provider
            status = "available"
            try:
                healthy = await provider.health_check()
            except Exception:
                healthy = False
            if not healthy:
                status = "unavailable"

            try:
                models = await provider.available_models()
            except Exception:
                models = []
            model_list = ", ".join(models) if models else "default configured model"
            default_marker = " (default)" if candidate.is_default else ""
            lines.append(f"- {provider.name}{default_marker}: {model_list} — {status}")
        return "\n".join(lines)

    async def _providers(self) -> str:
        lines = ["Connected providers:"]
        for candidate in self._provider_manager.fallback_candidates():
            try:
                healthy = await candidate.provider.health_check()
            except Exception:
                healthy = False
            status = "available" if healthy else "unavailable"
            default_marker = " (default)" if candidate.is_default else ""
            lines.append(f"- {candidate.provider.name}{default_marker}: {status}")
        return "\n".join(lines)

    def _tools(self) -> str:
        lines = ["Available tools:"]
        for definition in self._skill_registry.definitions():
            lines.append(f"- `{definition.name}` — {definition.description}")
        return "\n".join(lines)
