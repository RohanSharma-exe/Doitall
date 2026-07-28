from doitall.knowledge.markdown_loader import MarkdownLoader


def test_markdown_loader(tmp_path):
    file = tmp_path / "README.md"

    file.write_text(
        "# Hello",
        encoding="utf-8",
    )

    loader = MarkdownLoader()

    documents = loader.load(str(file))

    assert len(documents) == 1
    assert documents[0].metadata["type"] == "markdown"
