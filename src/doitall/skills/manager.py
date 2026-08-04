"""Skill execution manager module."""

import inspect
from typing import Any

from doitall.services.container import ServiceContainer
from doitall.skills.base import BaseSkill
from doitall.skills.registry import SkillRegistry


class SkillManager:
    """Executes registered skills by resolving their dependencies from ServiceContainer."""

    def __init__(
        self,
        registry: SkillRegistry,
        container: ServiceContainer,
    ) -> None:
        """Initialize SkillManager with registry and dependency container."""
        self._registry = registry
        self._container = container

    async def execute(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """Instantiate skill class, inject dependencies, validate status, and execute."""
        skill = self._create_skill(name)

        self._validate(skill)

        return await self._execute(
            skill,
            **kwargs,
        )

    def _create_skill(
        self,
        name: str,
    ) -> BaseSkill:
        skill_class = self._registry.get(name)

        signature = inspect.signature(skill_class.__init__)

        dependencies: list[Any] = []

        for parameter in list(signature.parameters.values())[1:]:
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            if parameter.annotation is not inspect.Parameter.empty:
                dependencies.append(
                    self._container.resolve_type(
                        parameter.annotation,
                    ),
                )
                continue

            dependencies.append(
                self._container.resolve(
                    parameter.name,
                ),
            )

        return skill_class(*dependencies)

    def _validate(
        self,
        skill: BaseSkill,
    ) -> None:
        if not skill.enabled:
            raise ValueError(
                f"Skill '{skill.name}' is disabled.",
            )

    async def _execute(
        self,
        skill: BaseSkill,
        **kwargs: Any,
    ) -> Any:
        return await skill.execute(**kwargs)
