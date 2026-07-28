from unittest.mock import Mock

from doitall.embeddings.manager import EmbeddingManager


def test_embed():
    service = Mock()

    service.embed.return_value = [1.0]

    manager = EmbeddingManager(service)

    assert manager.embed("hello") == [1.0]

    service.embed.assert_called_once_with("hello")


def test_embed_batch():
    service = Mock()

    service.embed_batch.return_value = [[1.0]]

    manager = EmbeddingManager(service)

    assert manager.embed_batch(["hello"]) == [[1.0]]

    service.embed_batch.assert_called_once_with(["hello"])
