"""Markdown file document loader module."""

from doitall.knowledge.document import Document
from doitall.knowledge.loader import DocumentLoader
from doitall.parsers.text_parser import TextParser


class MarkdownLoader(DocumentLoader):
    """Loader parsing Markdown (.md, .markdown) files into Document instances."""

    def __init__(self) -> None:
        """Initialize MarkdownLoader with TextParser dependency."""
        self.parser = TextParser()

    def load(
        self,
        path: str,
    ) -> list[Document]:
        """Parse Markdown document at file path and tag metadata with type='markdown'."""
        documents = self.parser.parse(path)

        for document in documents:
            document.metadata["type"] = "markdown"

        return documents

