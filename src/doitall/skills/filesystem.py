"""Safe workspace filesystem operations skill module."""

import asyncio
import functools
from collections.abc import Callable
from fnmatch import fnmatch
from typing import Any

from doitall.config.settings import settings
from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill
from doitall.workspace.workspace import Workspace

_ACTIONS = ("read", "write", "delete", "list", "exists")
_REQUIRES_PATH = {"read", "write", "delete", "exists"}  # "list" defaults to "."


class FilesystemSkill(BaseSkill):
    """Safe filesystem operations."""

    name = "filesystem"

    description = "Read, write, list, delete and inspect files."

    capabilities = ("filesystem",)

    @classmethod
    def definition(cls) -> ToolDefinition:
        """Return tool definition schema for filesystem operations skill."""
        return ToolDefinition(
            name=cls.name,
            description=cls.description,
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Filesystem action.",
                        "enum": list(_ACTIONS),
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
        **kwargs: Any,
    ) -> Any:
        """Execute a filesystem operation."""
        action = kwargs.get("action")

        if not isinstance(action, str):
            raise ValueError("'action' is required for filesystem operations.")

        handlers: dict[str, Callable[..., Any]] = {
            "read": self._read,
            "write": self._write,
            "delete": self._delete,
            "list": self._list,
            "exists": self._exists,
        }

        if action not in handlers:
            raise ValueError(f"Unknown filesystem action: {action}")

        if action in _REQUIRES_PATH and not kwargs.get("path"):
            raise ValueError(f"'path' is required for action '{action}'.")
        if action == "write" and "content" not in kwargs:
            raise ValueError("'content' is required for action 'write'.")

        # Run the synchronous handler in a thread pool so the event loop is
        # never blocked by filesystem I/O.
        handler = handlers[action]
        handler_kwargs = {
            key: value for key, value in kwargs.items() if key != "action"
        }

        return await asyncio.to_thread(functools.partial(handler, **handler_kwargs))

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

        max_write_bytes = getattr(
            settings,
            "FILESYSTEM_MAX_WRITE_BYTES",
            settings.FILESYSTEM_MAX_READ_BYTES,
        )
        if len(content.encode("utf-8")) > max_write_bytes:
            raise PermissionError(
                "Content is too large to write through the filesystem tool."
            )

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

        parts = [p for p in normalized.split("/") if p not in ("", ".")]
        if any(part == ".." for part in parts):
            raise PermissionError("Path traversal ('..') is not allowed.")

        # Check the full path, every ancestor prefix, and every individual
        # segment against each deny pattern — not just the first segment —
        # so patterns like ".env" or ".git" catch nested matches too
        # (e.g. "configs/.env", "sub/.git/config").
        candidates = {normalized}
        prefix = ""
        for part in parts:
            prefix = f"{prefix}/{part}" if prefix else part
            candidates.add(prefix)
            candidates.add(part)

        for pattern in settings.FILESYSTEM_DENY_PATTERNS:
            if any(fnmatch(candidate, pattern) for candidate in candidates):
                raise PermissionError("Path is denied by filesystem tool policy.")
