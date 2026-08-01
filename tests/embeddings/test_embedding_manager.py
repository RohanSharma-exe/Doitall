from unittest.mock import AsyncMock, Mock

import pytest

from doitall.embeddings.manager import EmbeddingManager


@pytest.mark.asyncio
async def test_embed():
    service = Mock()
    service.embed = AsyncMock()
    service.embed.return_value = [1.0]

    manager = EmbeddingManager(service)

    result = await manager.embed("hello")
    assert result == [1.0]

    service.embed.assert_called_once_with("hello")


@pytest.mark.asyncio
async def test_embed_batch():
    service = Mock()
    service.embed_batch = AsyncMock()
    service.embed_batch.return_value = [[1.0]]

    manager = EmbeddingManager(service)

    result = await manager.embed_batch(["hello"])
    assert result == [[1.0]]

    service.embed_batch.assert_called_once_with(["hello"])
