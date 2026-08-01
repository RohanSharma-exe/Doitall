import asyncio
import functools
from fnmatch import fnmatch
from typing import Any

from doitall.config.settings import settings
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

        # Run the synchronous handler in a thread pool so the event loop is
        # never blocked by filesystem I/O.
        handler = handlers[action]
        return await asyncio.to_thread(functools.partial(handler, **kwargs))

    def _read(
        self,
        path: str,
    ) -> str:
        self._ensure_allowed(path)
        resolved = self._workspace.resolve(path)
        if resolved.stat().st_size > settings.FILESYSTEM_MAX_READ_BYTES:
            raise PermissionError(
                "File is too large to read through the filesystem tool."
            )
        data = resolved.read_bytes()
        if b"\x00" in data:
            raise PermissionError(
                "Binary files cannot be read through the filesystem tool."
            )
        return data.decode("utf-8")

    def _write(
        self,
        path: str,
        content: str,
    ) -> bool:
        if not settings.ENABLE_FILESYSTEM_WRITE_TOOLS:
            raise PermissionError("Filesystem writes are disabled.")

        self._ensure_allowed(path)
        self._workspace.write_text(
            path,
            content,
        )
        return True

    def _delete(
        self,
        path: str,
    ) -> bool:
        if not settings.ENABLE_FILESYSTEM_WRITE_TOOLS:
            raise PermissionError("Filesystem deletes are disabled.")

        self._ensure_allowed(path)
        self._workspace.delete(path)
        return True

    def _list(
        self,
        path: str = ".",
    ) -> list[str]:
        self._ensure_allowed(path)
        files = self._workspace.list_files(path)
        if len(files) > settings.FILESYSTEM_MAX_LIST_ENTRIES:
            raise PermissionError("Directory contains too many entries to list safely.")
        return [str(file.relative_to(self._workspace.root)) for file in files]

    def _exists(
        self,
        path: str,
    ) -> bool:
        self._ensure_allowed(path)
        return self._workspace.exists(path)

    def _ensure_allowed(self, path: str = ".") -> None:
        normalized = str(path).replace("\\", "/").lstrip("/") or "."
        for pattern in settings.FILESYSTEM_DENY_PATTERNS:
            if fnmatch(normalized, pattern) or fnmatch(
                normalized.split("/", 1)[0], pattern
            ):
                raise PermissionError("Path is denied by filesystem tool policy.")
