"""Safe API error helpers.

This module keeps detailed exception information in server logs while returning
stable, user-safe error payloads from public endpoints.
"""

from fastapi import HTTPException


def public_http_error(status_code: int, detail: str) -> HTTPException:
    """Build a public HTTPException with a sanitized message."""
    return HTTPException(status_code=status_code, detail=detail)


CHAT_FAILED = "Chat request failed."
STREAM_FAILED = "Chat stream failed."
INGEST_FAILED = "Knowledge ingestion failed."
