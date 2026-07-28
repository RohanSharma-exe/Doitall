from doitall.parsers.text_parser import TextParser


def test_text_parser(tmp_path):
    file = tmp_path / "hello.txt"

    file.write_text(
        "Hello Parser",
        encoding="utf-8",
    )

    parser = TextParser()

    documents = parser.parse(str(file))

    assert len(documents) == 1
    assert documents[0].content == "Hello Parser"
