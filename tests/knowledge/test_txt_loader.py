from doitall.knowledge.txt_loader import TxtLoader


def test_txt_loader(tmp_path):
    file = tmp_path / "hello.txt"

    file.write_text(
        "Hello Doitall",
        encoding="utf-8",
    )

    loader = TxtLoader()

    documents = loader.load(str(file))

    assert len(documents) == 1
    assert documents[0].content == "Hello Doitall"
