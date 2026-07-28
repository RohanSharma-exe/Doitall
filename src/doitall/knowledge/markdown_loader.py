from doitall.knowledge.document import Document
from doitall.knowledge.loader import DocumentLoader
from doitall.parsers.text_parser import TextParser


class MarkdownLoader(DocumentLoader):
    def __init__(self) -> None:
        self.parser = TextParser()

    def load(
        self,
        path: str,
    ) -> list[Document]:
        documents = self.parser.parse(path)

        for document in documents:
            document.metadata["type"] = "markdown"

        return documents
