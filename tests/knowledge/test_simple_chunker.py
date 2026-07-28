from doitall.knowledge.document import Document
from doitall.knowledge.simple_chunker import SimpleChunker


def test_simple_chunker():
    document = Document(content="A" * 1200)

    chunker = SimpleChunker(chunk_size=500)

    chunks = chunker.chunk(document)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2
