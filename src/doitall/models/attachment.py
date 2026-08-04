"""File and media attachment data models."""

from enum import StrEnum

from pydantic import BaseModel


class AttachmentType(StrEnum):
    """Supported file attachment media types."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    OTHER = "other"


class Attachment(BaseModel):
    """File attachment associated with a prompt or message."""

    type: AttachmentType
    name: str
    path: str
    mime_type: str | None = None
    size: int | None = None

