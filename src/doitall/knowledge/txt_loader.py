"""Plain text file document loader module."""

from doitall.knowledge.loader import DocumentLoader
from doitall.parsers.text_parser import TextParser


class TxtLoader(DocumentLoader):
    """Loader parsing plain text (.txt) files into Document instances."""

    def __init__(self) -> None:
        """Initialize TxtLoader with TextParser dependency."""
        self.parser = TextParser()

    def load(
        self,
        path: str,
    ) -> list:
        """Parse plain text document at file path."""
        return self.parser.parse(path)
