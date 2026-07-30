from unittest.mock import AsyncMock, Mock

import pytest

from doitall.core.exceptions import ProviderError, ValidationError
from doitall.knowledge.document import Document
from doitall.knowledge.ingestion import KnowledgeIngestionService


def _make_service(add_side_effect=None):
    repository = Mock()
    if add_side_effect:
        repository.add = AsyncMock(side_effect=add_side_effect)
    else:
        repository.add = AsyncMock()
    return KnowledgeIngestionService(repository), repository


@pytest.mark.asyncio
async def test_ingest_valid_document():
    service, repo = _make_service()
    repo.add.return_value = 1
    doc = Document(content="Valid content")
    result = await service.ingest(doc)
    repo.add.assert_called_once_with(doc)
    assert result.document_id == doc.id
    assert result.chunk_count == 1


@pytest.mark.asyncio
async def test_ingest_empty_content_raises():
    service, repo = _make_service()
    with pytest.raises(ValidationError, match="cannot be empty"):
        await service.ingest(Document(content=""))


@pytest.mark.asyncio
async def test_ingest_whitespace_only_raises():
    service, repo = _make_service()
    with pytest.raises(ValidationError, match="cannot be empty"):
        await service.ingest(Document(content="   \n\t"))


@pytest.mark.asyncio
async def test_ingest_many_calls_add_for_each():
    service, repo = _make_service()
    repo.add.return_value = 1
    docs = [Document(content="One"), Document(content="Two"), Document(content="Three")]
    results = await service.ingest_many(docs)
    assert repo.add.call_count == 3
    assert len(results) == 3


@pytest.mark.asyncio
async def test_ingest_many_empty_list_is_noop():
    service, repo = _make_service()
    results = await service.ingest_many([])
    repo.add.assert_not_called()
    assert results == []


@pytest.mark.asyncio
async def test_ingest_many_partial_failure_raises_provider_error():
    """If some docs fail, ingest_many must raise ProviderError listing the failed IDs."""

    call_count = 0

    async def add_side_effect(doc):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("Simulated failure")

    service, repo = _make_service(add_side_effect=add_side_effect)

    docs = [
        Document(content="Good doc one"),
        Document(content="Bad doc two"),
        Document(content="Good doc three"),
    ]

    with pytest.raises(ProviderError, match="Failed to ingest 1 out of 3"):
        await service.ingest_many(docs)


@pytest.mark.asyncio
async def test_ingest_many_all_fail_raises_provider_error():
    service, repo = _make_service(add_side_effect=RuntimeError("Always fails"))

    docs = [Document(content="A"), Document(content="B")]

    with pytest.raises(ProviderError, match="Failed to ingest 2 out of 2"):
        await service.ingest_many(docs)
