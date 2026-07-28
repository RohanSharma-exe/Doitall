from doitall.knowledge.chunk import Chunk
from doitall.serialization.chunk_serializer import ChunkSerializer


def test_chunk_serializer_round_trip():
    chunk = Chunk(
        document_id="doc1",
        text="Hello",
        chunk_index=0,
    )

    payload = ChunkSerializer.to_payload(chunk)

    restored = ChunkSerializer.from_payload(
        chunk.id,
        payload,
    )

    assert restored.id == chunk.id
    assert restored.text == chunk.text
    assert restored.document_id == chunk.document_id
