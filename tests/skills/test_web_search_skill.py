import pytest

from doitall.skills.web_search import WebFetchSkill, WebSearchSkill


def test_web_search_definition():
    definition = WebSearchSkill.definition()

    assert definition.name == "web_search"
    assert "query" in definition.input_schema["properties"]


def test_web_fetch_definition():
    definition = WebFetchSkill.definition()

    assert definition.name == "web_fetch"
    assert "url" in definition.input_schema["properties"]


@pytest.mark.asyncio
async def test_web_fetch_rejects_non_http_url():
    with pytest.raises(ValueError):
        await WebFetchSkill().execute(url="file:///etc/passwd")
