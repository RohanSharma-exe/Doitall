"""Sandboxed project workspace manager module."""

import shutil
from pathlib import Path


class Workspace:
    """Represents a sandboxed project workspace."""

    def __init__(
        self,
        root: str | Path,
    ) -> None:
        """Initialize workspace with root directory path."""
        self._root = Path(root).resolve()

    @property
    def root(self) -> Path:
        """Return resolved absolute root Path of workspace."""
        return self._root

    def resolve(
        self,
        relative_path: str | Path,
    ) -> Path:
        """Resolve relative path into absolute Path, raising ValueError if path escapes workspace root."""
        path = (self._root / relative_path).resolve()

        try:
            path.relative_to(self._root)
        except ValueError as exc:
            raise ValueError("Path escapes workspace.") from exc

        return path


    def exists(
        self,
        relative_path: str | Path,
    ) -> bool:
        return self.resolve(relative_path).exists()

    def mkdir(
        self,
        relative_path: str | Path,
        *,
        parents: bool = True,
        exist_ok: bool = True,
    ) -> Path:
        path = self.resolve(relative_path)
        path.mkdir(
            parents=parents,
            exist_ok=exist_ok,
        )
        return path

    def read_text(
        self,
        relative_path: str | Path,
        encoding: str = "utf-8",
    ) -> str:
        return self.resolve(relative_path).read_text(
            encoding=encoding,
        )

    def write_text(
        self,
        relative_path: str | Path,
        content: str,
        encoding: str = "utf-8",
    ) -> Path:
        path = self.resolve(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding=encoding,
        )

        return path

    def delete(
        self,
        relative_path: str | Path,
    ) -> None:
        path = self.resolve(relative_path)

        if not path.exists():
            return

        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def list_files(
        self,
        relative_path: str | Path = ".",
    ) -> list[Path]:
        path = self.resolve(relative_path)

        return sorted(path.iterdir())

    def copy(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> Path:
        src = self.resolve(source)
        dst = self.resolve(destination)

        dst.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            src,
            dst,
        )

        return dst

    def move(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> Path:
        src = self.resolve(source)
        dst = self.resolve(destination)

        dst.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(src),
            str(dst),
        )

        return dst
