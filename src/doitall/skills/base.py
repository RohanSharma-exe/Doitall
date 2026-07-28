from abc import ABC, abstractmethod
from typing import Any

from doitall.models.tool_definition import ToolDefinition


class BaseSkill(ABC):
    """Base class for all executable skills."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    enabled: bool = True

    @abstractmethod
    async def execute(
        self,
        **kwargs: Any,
    ) -> Any:
        """Execute the skill."""
        raise NotImplementedError

    @classmethod
    def definition(cls) -> ToolDefinition:
        """Return tool metadata."""

        return ToolDefinition(
            name=cls.name,
            description=cls.description,
            input_schema={},
        )
