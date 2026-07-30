from unittest.mock import AsyncMock, Mock

import pytest

from doitall.knowledge.document import Document
from doitall.runtime.context import RuntimeContext
from doitall.runtime.knowledge_provider import KnowledgeProvider


@pytest.mark.asyncio
async def test_populate():
    repository = Mock()
    repository.search = AsyncMock(return_value=[
        Document(
            content="Python",
        )
    ])

    provider = KnowledgeProvider(repository)

    context = RuntimeContext(query="python")

    await provider.populate(context)

    assert len(context.knowledge) == 1
    assert context.knowledge[0].content == "Python"


@pytest.mark.asyncio
async def test_repository_called():
    repository = Mock()
    repository.search = AsyncMock(return_value=[])

    provider = KnowledgeProvider(repository)

    context = RuntimeContext(query="hello")

    await provider.populate(context)

    repository.search.assert_called_once_with(context.query)


@pytest.mark.asyncio
async def test_empty_query_skips_search():
    """KnowledgeProvider should not call search when query is empty."""
    repository = Mock()
    repository.search = AsyncMock()

    provider = KnowledgeProvider(repository)

    context = RuntimeContext(query="")

    await provider.populate(context)

    repository.search.assert_not_called()
    assert context.knowledge == []
