"""Execution helpers for slash commands submitted through chat."""

from dataclasses import dataclass
from shlex import split

from doitall.commands import CommandRegistry
from doitall.providers.manager import ProviderManager
from doitall.skills.manager import SkillManager
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
        providers: ProviderManager,
        skills: SkillRegistry,
        skill_manager: SkillManager | None = None,
    ):
        self._registry = registry
        self._provider_manager = providers
        self._skill_registry = skills
        self._skill_manager = skill_manager

    def is_command(self, content: str) -> bool:
        return content.strip().startswith("/")

    async def execute(self, content: str) -> CommandResult | None:
        parts = split(content.strip())
        if not parts:
            return None

        command_name = parts[0]
        arguments = parts[1:]
        try:
            command = self._registry.get(command_name)
        except KeyError:
            return CommandResult(
                content=f"Unknown command `{command_name}`. Try `/help` to see available commands."
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

        tool_map = {
            "/calculator": ("calculator", self._calculator_args),
            "/time": ("time", self._time_args),
            "/filesystem": ("filesystem", self._filesystem_args),
            "/web-search": ("web_search", self._web_search_args),
            "/web-fetch": ("web_fetch", self._web_fetch_args),
        }

        tool = tool_map.get(command_name)

        if tool:
            skill_name, argument_builder = tool

            if not self._skill_registry.exists(skill_name):
                return CommandResult(
                    content=f"Skill '{skill_name}' is not registered."
                )

            kwargs = argument_builder(arguments)

            if self._skill_manager is None:
                return CommandResult(
                    content="Skill execution is not available."
                )

            result = await self._skill_manager.execute(
                skill_name,
                **kwargs,
            )

            return CommandResult(content=str(result))

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

    def _calculator_args(
        self,
        arguments: list[str],
    ) -> dict[str, str]:
        if not arguments:
            raise ValueError(
                "Usage: /calculator <expression>"
            )

        return {
            "expression": " ".join(arguments),
        }


    def _time_args(
        self,
        arguments: list[str],
    ) -> dict[str, str]:
        return {
            "timezone": arguments[0] if arguments else "UTC",
        }


    def _web_search_args(
        self,
        arguments: list[str],
    ) -> dict[str, str]:
        if not arguments:
            raise ValueError(
                "Usage: /web-search <query>"
            )

        return {
            "query": " ".join(arguments),
        }


    def _web_fetch_args(
        self,
        arguments: list[str],
    ) -> dict[str, str]:
        if not arguments:
            raise ValueError(
                "Usage: /web-fetch <url>"
            )

        return {
            "url": arguments[0],
        }


    def _filesystem_args(
        self,
        arguments: list[str],
    ) -> dict:
        if not arguments:
            raise ValueError(
                "Usage: /filesystem <action> [path] [content]"
            )

        action = arguments[0]

        if action == "list":
            return {
                "action": "list",
                "path": arguments[1] if len(arguments) > 1 else ".",
            }

        if action in {"read", "exists", "delete"}:
            if len(arguments) < 2:
                raise ValueError(
                    f"Usage: /filesystem {action} <path>"
                )

            return {
                "action": action,
                "path": arguments[1],
            }

        if action == "write":
            if len(arguments) < 3:
                raise ValueError(
                    "Usage: /filesystem write <path> <content>"
                )

            return {
                "action": "write",
                "path": arguments[1],
                "content": " ".join(arguments[2:]),
            }

        raise ValueError(
            f"Unknown filesystem action: {action}"
        )
