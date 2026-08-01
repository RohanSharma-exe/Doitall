from doitall.core.exceptions import SkillError
from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill


class SkillRegistry:
    """Registry for executable skills."""

    def __init__(self) -> None:
        self._skills: dict[str, type[BaseSkill]] = {}

    def names(self) -> list[str]:
        return list(self._skills.keys())

    def register(
        self,
        skill: type[BaseSkill],
    ) -> None:
        self._skills[skill.name] = skill

    def unregister(
        self,
        name: str,
    ) -> None:
        self._skills.pop(name, None)

    def get(
        self,
        name: str,
    ) -> type[BaseSkill]:
        if name not in self._skills:
            raise SkillError(
                f"Unknown skill: '{name}'. Available skills: {sorted(self._skills)}"
            )
        return self._skills[name]

    def exists(
        self,
        name: str,
    ) -> bool:
        return name in self._skills

    def all(
        self,
    ) -> list[type[BaseSkill]]:
        return list(self._skills.values())

    def definitions(
        self,
    ) -> list[ToolDefinition]:
        """Return definitions for all registered skills."""

        return [skill.definition() for skill in self._skills.values()]

    def definition(
        self,
        name: str,
    ) -> ToolDefinition:
        """Return the definition for a single skill."""

        return self.get(name).definition()

    def clear(self) -> None:
        self._skills.clear()
