from doitall.knowledge.chunk import Chunk


def test_chunk():
    chunk = Chunk(
        document_id="1",
        text="Hello",
        chunk_index=0,
    )

    assert chunk.chunk_index == 0
