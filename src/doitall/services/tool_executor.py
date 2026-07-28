from typing import Any

from doitall.skills.manager import SkillManager


class ToolExecutor:
    """Executes tools using the SkillManager."""

    def __init__(
        self,
        skill_manager: SkillManager,
    ) -> None:
        self._skill_manager = skill_manager

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Execute a tool."""

        return await self._skill_manager.execute(
            name,
            **arguments,
        )
