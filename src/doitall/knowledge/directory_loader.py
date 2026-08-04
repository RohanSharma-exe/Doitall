"""Directory document loader module for recursive file loading."""

from pathlib import Path

from doitall.knowledge.document import Document
from doitall.knowledge.loader import DocumentLoader
from doitall.knowledge.loader_registry import LoaderRegistry
from doitall.knowledge.markdown_loader import MarkdownLoader
from doitall.knowledge.txt_loader import TxtLoader


class DirectoryLoader(DocumentLoader):
    """Recursively scans directories and loads documents using extension-registered loaders."""

    def __init__(
        self,
        registry: LoaderRegistry | None = None,
    ) -> None:
        """Initialize directory loader and register default .txt and .md file loaders."""
        self.registry = registry or LoaderRegistry()

        if ".txt" not in self.registry.extensions:
            self.registry.register(
                ".txt",
                TxtLoader(),
            )

        if ".md" not in self.registry.extensions:
            self.registry.register(
                ".md",
                MarkdownLoader(),
            )

        if ".markdown" not in self.registry.extensions:
            self.registry.register(
                ".markdown",
                MarkdownLoader(),
            )

    def load(
        self,
        path: str,
    ) -> list[Document]:
        """Recursively scan path directory and load documents using matching loaders."""
        documents: list[Document] = []

        for file in Path(path).rglob("*"):
            if not file.is_file():
                continue

            loader = self.registry.get(file.suffix)

            if loader is None:
                continue

            documents.extend(loader.load(str(file)))

        return documents
