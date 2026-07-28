from doitall.models.attachment import (
    Attachment,
    AttachmentType,
)
from doitall.models.prompt import Prompt
from doitall.models.tool import (
    Tool,
    ToolParameter,
)


def test_prompt_defaults():
    prompt = Prompt(
        user_prompt="Hello",
    )

    assert prompt.system_prompt is None
    assert prompt.user_prompt == "Hello"
    assert prompt.attachments == []
    assert prompt.tools == []
    assert prompt.temperature == 0.7
    assert prompt.top_p == 1.0
    assert prompt.max_tokens is None


def test_prompt_with_tool_and_attachment():
    attachment = Attachment(
        type=AttachmentType.IMAGE,
        name="cat.png",
        path="uploads/cat.png",
    )

    tool = Tool(
        name="describe_image",
        description="Describe an image",
        parameters=[
            ToolParameter(
                name="image",
                type="string",
            )
        ],
    )

    prompt = Prompt(
        system_prompt="You are a helpful assistant.",
        user_prompt="Describe this image.",
        attachments=[attachment],
        tools=[tool],
        temperature=0.2,
        top_p=0.9,
        max_tokens=512,
    )

    assert len(prompt.attachments) == 1
    assert len(prompt.tools) == 1
    assert prompt.temperature == 0.2
    assert prompt.top_p == 0.9
    assert prompt.max_tokens == 512
