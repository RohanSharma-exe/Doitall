from enum import StrEnum

from pydantic import BaseModel


class AttachmentType(StrEnum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    OTHER = "other"


class Attachment(BaseModel):
    type: AttachmentType
    name: str
    path: str
    mime_type: str | None = None
    size: int | None = None
