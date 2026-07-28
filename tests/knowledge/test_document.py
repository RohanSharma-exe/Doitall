from doitall.knowledge.document import Document


def test_document():
    document = Document(
        content="Hello",
    )

    assert document.content == "Hello"
