from unittest.mock import Mock, call

from doitall.knowledge.document import Document
from doitall.knowledge.ingestion import KnowledgeIngestionService


def test_ingest_many():
    repository = Mock()

    service = KnowledgeIngestionService(repository)

    documents = [
        Document(content="One"),
        Document(content="Two"),
    ]

    service.ingest_many(documents)

    repository.add.assert_has_calls(
        [
            call(documents[0]),
            call(documents[1]),
        ]
    )

    assert repository.add.call_count == 2
