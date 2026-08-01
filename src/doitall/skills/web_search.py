"""Web search and page fetch skills."""

from typing import Any
from urllib.parse import urlparse

import httpx

from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill


class WebSearchSkill(BaseSkill):
    """Searches the web using DuckDuckGo Instant Answer API."""

    name = "web_search"
    description = "Search the web for current information and return concise results."

    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.name,
            description=cls.description,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return.",
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        )

    async def execute(self, *, query: str, limit: int = 5) -> dict[str, Any]:
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty.")

        limit = max(1, min(limit, 10))
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1,
                },
            )
            response.raise_for_status()
            payload = response.json()

        results: list[dict[str, str]] = []
        abstract_url = payload.get("AbstractURL")
        if payload.get("AbstractText") and abstract_url:
            results.append(
                {
                    "title": payload.get("Heading") or query,
                    "url": abstract_url,
                    "snippet": payload["AbstractText"],
                }
            )

        for topic in payload.get("RelatedTopics", []):
            self._collect_topic(topic, results, limit)
            if len(results) >= limit:
                break

        return {"query": query, "results": results[:limit]}

    def _collect_topic(
        self, topic: dict[str, Any], results: list[dict[str, str]], limit: int
    ) -> None:
        if len(results) >= limit:
            return
        if "Topics" in topic:
            for nested in topic["Topics"]:
                self._collect_topic(nested, results, limit)
                if len(results) >= limit:
                    return
            return
        url = topic.get("FirstURL")
        text = topic.get("Text")
        if url and text:
            results.append({"title": text.split(" - ", 1)[0], "url": url, "snippet": text})


class WebFetchSkill(BaseSkill):
    """Fetches text from an HTTP(S) URL."""

    name = "web_fetch"
    description = "Fetch the text content of a public HTTP or HTTPS URL."

    @classmethod
    def definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.name,
            description=cls.description,
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "HTTP or HTTPS URL."},
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return.",
                        "minimum": 200,
                        "maximum": 12000,
                    },
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        )

    async def execute(self, *, url: str, max_chars: int = 4000) -> dict[str, Any]:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Only absolute http(s) URLs are supported.")
        max_chars = max(200, min(max_chars, 12000))

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            text = response.text

        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "content_type": content_type,
            "text": text[:max_chars],
            "truncated": len(text) > max_chars,
        }
