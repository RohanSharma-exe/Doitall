from typing import Any

from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill
from doitall.workspace.workspace import Workspace


class FilesystemSkill(BaseSkill):
    """Safe filesystem operations."""

    name = "filesystem"
    description = "Read, write, list, delete and inspect files."

    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.name,
            description=cls.description,
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Filesystem action.",
                    },
                    "path": {
                        "type": "string",
                        "description": "Relative workspace path.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write.",
                    },
                },
                "required": [
                    "action",
                ],
                "additionalProperties": False,
            },
        )

    def __init__(
        self,
        workspace: Workspace,
    ) -> None:
        self._workspace = workspace

    async def execute(
        self,
        action: str,
        **kwargs: Any,
    ) -> Any:
        handlers = {
            "read": self._read,
            "write": self._write,
            "delete": self._delete,
            "list": self._list,
            "exists": self._exists,
        }

        if action not in handlers:
            raise ValueError(f"Unknown filesystem action: {action}")

        return handlers[action](**kwargs)

    def _read(
        self,
        path: str,
    ) -> str:
        return self._workspace.read_text(path)

    def _write(
        self,
        path: str,
        content: str,
    ) -> bool:
        self._workspace.write_text(
            path,
            content,
        )
        return True

    def _delete(
        self,
        path: str,
    ) -> bool:
        self._workspace.delete(path)
        return True

    def _list(
        self,
        path: str = ".",
    ) -> list[str]:
        return [
            str(file.relative_to(self._workspace.root))
            for file in self._workspace.list_files(path)
        ]

    def _exists(
        self,
        path: str,
    ) -> bool:
        return self._workspace.exists(path)
