from doitall.models.attachment import (
    Attachment,
    AttachmentType,
)


def test_attachment():
    attachment = Attachment(
        type=AttachmentType.IMAGE,
        name="image.png",
        path="uploads/image.png",
        mime_type="image/png",
        size=1024,
    )

    assert attachment.type == AttachmentType.IMAGE
    assert attachment.name == "image.png"
    assert attachment.path == "uploads/image.png"
    assert attachment.mime_type == "image/png"
    assert attachment.size == 1024


def test_attachment_defaults():
    attachment = Attachment(
        type=AttachmentType.DOCUMENT,
        name="resume.pdf",
        path="uploads/resume.pdf",
    )

    assert attachment.mime_type is None
    assert attachment.size is None
