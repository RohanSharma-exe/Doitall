from pathlib import Path

from doitall.knowledge.document import Document
from doitall.parsers.parser import DocumentParser


class TextParser(DocumentParser):
    def parse(
        self,
        path: str,
    ) -> list[Document]:
        return [
            Document(
                content=Path(path).read_text(
                    encoding="utf-8",
                ),
                source=path,
            )
        ]
