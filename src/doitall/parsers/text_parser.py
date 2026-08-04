"""Plain text document parser module."""

from pathlib import Path

from doitall.knowledge.document import Document
from doitall.parsers.parser import DocumentParser


class TextParser(DocumentParser):
    """Parser reading UTF-8 text files into Document objects."""

    def parse(
        self,
        path: str,
    ) -> list[Document]:
        """Read file at path as UTF-8 text string and wrap in Document."""
        return [
            Document(
                content=Path(path).read_text(
                    encoding="utf-8",
                ),
                source=path,
            )
        ]
