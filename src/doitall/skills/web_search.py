"""Web search and page fetch skills."""

import ipaddress
import re
import socket
from typing import Any
from urllib.parse import unquote, urlparse

import httpx

from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/138.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# SSRF protection — private / link-local / loopback ranges
# ---------------------------------------------------------------------------

_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / AWS metadata
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique-local
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]


def _is_ssrf_blocked(host: str) -> bool:
    """Return True if the resolved IP of *host* falls in a private/internal range.

    DNS is resolved here so that DNS-rebinding attacks (public hostname →
    private IP) are also caught.
    """
    try:
        # Resolve to a list of (family, type, proto, canonname, sockaddr) tuples
        infos = socket.getaddrinfo(host, None)
    except OSError:
        # Unresolvable host — let httpx surface the DNS error naturally.
        return False

    for info in infos:
        addr = info[4][0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            continue
        for network in _PRIVATE_NETWORKS:
            if ip in network:
                return True
    return False


_RESULT_BLOCK_RE = re.compile(
    r'<a rel="nofollow" class="result__a" href="(?P<url>[^"]+)">(?P<title>.*?)</a>'
    r'.*?class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
    re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")


def _clean_html_text(fragment: str) -> str:
    text = _TAG_RE.sub("", fragment)
    return re.sub(r"\s+", " ", text).strip()


def _unwrap_ddg_redirect(url: str) -> str:
    # DDG HTML results wrap outbound links as //duckduckgo.com/l/?uddg=<encoded>&...
    if "uddg=" in url:
        try:
            encoded = url.split("uddg=", 1)[1].split("&", 1)[0]
            return unquote(encoded)
        except Exception:
            return url
    return url


class WebSearchSkill(BaseSkill):
    """Searches the web using DuckDuckGo's HTML results page.

    Note: this scrapes a public HTML endpoint rather than calling a
    documented API, so the markup could change and break the parser.
    For a more stable/production setup, swap this out for a proper
    search API (Brave Search API, Tavily, Serper, etc.) that returns
    structured JSON and doesn't rely on parsing HTML.
    """

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

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        query: str = kwargs["query"]
        limit: int = kwargs.get("limit", 5)
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty.")

        limit = max(1, min(limit, 10))

        try:
            async with httpx.AsyncClient(
                timeout=10.0, follow_redirects=True, headers={"User-Agent": _UA}
            ) as client:
                response = await client.post(
                    "https://html.duckduckgo.com/html/",
                    data={"q": query},
                )
                response.raise_for_status()
                html = response.text
        except httpx.HTTPError as exc:
            return {"query": query, "results": [], "error": str(exc)}

        results: list[dict[str, str]] = []
        for match in _RESULT_BLOCK_RE.finditer(html):
            if len(results) >= limit:
                break
            url = _unwrap_ddg_redirect(match.group("url"))
            title = _clean_html_text(match.group("title"))
            snippet = _clean_html_text(match.group("snippet"))
            if url and title:
                results.append({"title": title, "url": url, "snippet": snippet})

        # BUG-N003: Distinguish a successful parse with no results from a
        # parser failure (DDG markup changed so the regex matched nothing).
        if not results and "result__a" not in html:
            # The page contained no recognisable result blocks at all —
            # treat this as a parse failure rather than "no results".
            return {
                "query": query,
                "results": [],
                "error": "parse_failure: no result blocks found in response HTML",
            }

        return {"query": query, "results": results}


class WebFetchSkill(BaseSkill):
    """Fetches readable text from an HTTP(S) URL."""

    name = "web_fetch"
    description = "Fetch the text content of a public HTTP or HTTPS URL."

    _TEXTUAL_TYPES = (
        "text/",
        "application/json",
        "application/xml",
        "application/xhtml",
    )

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

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        url: str = kwargs["url"]
        max_chars: int = kwargs.get("max_chars", 4000)
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Only absolute http(s) URLs are supported.")
        max_chars = max(200, min(max_chars, 12000))

        # BUG-N007: SSRF protection — block requests to private / internal IPs.
        # Hostname is resolved here (not by httpx) so DNS-rebinding is also caught.
        host = parsed.hostname or ""
        if host and _is_ssrf_blocked(host):
            return {
                "url": url,
                "error": "blocked: target resolves to a private or link-local address",
            }

        try:
            async with httpx.AsyncClient(
                timeout=10.0, follow_redirects=True, headers={"User-Agent": _UA}
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            return {"url": url, "error": str(exc)}

        content_type = response.headers.get("content-type", "")
        if not any(t in content_type for t in self._TEXTUAL_TYPES):
            return {
                "url": str(response.url),
                "status_code": response.status_code,
                "content_type": content_type,
                "text": "",
                "truncated": False,
                "note": "Skipped: non-textual content type.",
            }

        raw_text = response.text
        if "html" in content_type:
            # Strip script/style blocks, then tags, to avoid dumping raw markup.
            no_scripts = re.sub(
                r"<(script|style)[^>]*>.*?</\1>",
                "",
                raw_text,
                flags=re.DOTALL | re.IGNORECASE,
            )
            text = _clean_html_text(no_scripts)
        else:
            text = raw_text

        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "content_type": content_type,
            "text": text[:max_chars],
            "truncated": len(text) > max_chars,
        }
