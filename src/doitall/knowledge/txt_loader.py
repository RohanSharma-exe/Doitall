from doitall.knowledge.loader import DocumentLoader
from doitall.parsers.text_parser import TextParser


class TxtLoader(DocumentLoader):
    def __init__(self) -> None:
        self.parser = TextParser()

    def load(
        self,
        path: str,
    ) -> list:
        return self.parser.parse(path)
