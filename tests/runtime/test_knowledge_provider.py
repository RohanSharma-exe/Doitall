from unittest.mock import Mock

from doitall.knowledge.document import Document
from doitall.runtime.context import RuntimeContext
from doitall.runtime.knowledge_provider import KnowledgeProvider


def test_populate():
    repository = Mock()

    repository.search.return_value = [
        Document(
            content="Python",
        )
    ]

    provider = KnowledgeProvider(repository)

    context = RuntimeContext()

    provider.populate(
        context,
        "python",
    )

    assert len(context.knowledge) == 1
    assert context.knowledge[0].content == "Python"


def test_repository_called():
    repository = Mock()

    repository.search.return_value = []

    provider = KnowledgeProvider(repository)

    provider.populate(
        RuntimeContext(),
        "hello",
    )

    repository.search.assert_called_once_with("hello")
