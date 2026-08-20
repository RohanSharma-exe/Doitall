from doitall.knowledge.chunk import Chunk


def test_chunk():
    chunk = Chunk(
        document_id="1",
        text="Hello",
        chunk_index=0,
    )

    assert chunk.chunk_index == 0


def test_chunk_id_is_deterministic():
    first = Chunk(document_id="doc-1", text="Hello", chunk_index=0)
    retry = Chunk(document_id="doc-1", text="Hello", chunk_index=0)

    assert first.id == retry.id


def test_chunk_id_changes_with_chunk_identity():
    original = Chunk(document_id="doc-1", text="Hello", chunk_index=0)

    assert Chunk(document_id="doc-2", text="Hello", chunk_index=0).id != original.id
    assert Chunk(document_id="doc-1", text="Hello", chunk_index=1).id != original.id
    assert Chunk(document_id="doc-1", text="Changed", chunk_index=0).id != original.id


def test_explicit_chunk_id_is_preserved():
    chunk = Chunk(id="existing-id", document_id="doc-1", text="Hello", chunk_index=0)

    assert chunk.id == "existing-id"
