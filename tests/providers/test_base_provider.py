import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.providers.base import BaseProvider


class ConcreteProvider(BaseProvider):
    """Minimal concrete implementation to test BaseProvider behaviour."""

    def __init__(self) -> None:
        super().__init__("test")

    async def chat(self, messages, **kwargs) -> ProviderResponse:
        return ProviderResponse(
            content="ok", tool_calls=[], finish_reason="stop", model="test"
        )

    async def health_check(self) -> bool:
        return True


def test_capabilities_defaults():
    provider = ConcreteProvider()
    caps = provider.capabilities()

    assert caps["chat"] is True
    assert caps["stream"] is False
    assert caps["embedding"] is False
    assert caps["image_understanding"] is False
    assert caps["image_generation"] is False
    assert caps["speech_to_text"] is False
    assert caps["text_to_speech"] is False
    assert caps["tool_call"] is False


@pytest.mark.asyncio
async def test_stream_raises_not_implemented():
    provider = ConcreteProvider()
    with pytest.raises(NotImplementedError, match="does not support streaming"):
        async for _ in provider.stream([]):
            pass


@pytest.mark.asyncio
async def test_embedding_raises_not_implemented():
    provider = ConcreteProvider()
    with pytest.raises(NotImplementedError, match="does not support embeddings"):
        await provider.embedding("some text")


@pytest.mark.asyncio
async def test_image_understanding_raises_not_implemented():
    provider = ConcreteProvider()
    with pytest.raises(NotImplementedError):
        await provider.image_understanding(image=None, prompt="describe")


@pytest.mark.asyncio
async def test_image_generation_raises_not_implemented():
    provider = ConcreteProvider()
    with pytest.raises(NotImplementedError):
        await provider.image_generation(prompt="draw a cat")


@pytest.mark.asyncio
async def test_speech_to_text_raises_not_implemented():
    provider = ConcreteProvider()
    with pytest.raises(NotImplementedError):
        await provider.speech_to_text(audio=b"")


@pytest.mark.asyncio
async def test_text_to_speech_raises_not_implemented():
    provider = ConcreteProvider()
    with pytest.raises(NotImplementedError):
        await provider.text_to_speech(text="hello")


@pytest.mark.asyncio
async def test_available_models_returns_empty_list():
    provider = ConcreteProvider()
    models = await provider.available_models()
    assert models == []


def test_name_set_correctly():
    provider = ConcreteProvider()
    assert provider.name == "test"


def test_abstract_class_cannot_be_instantiated_without_chat():
    """BaseProvider without chat() implemented must raise TypeError."""

    class BadProvider(BaseProvider):
        async def health_check(self) -> bool:
            return True

    with pytest.raises(TypeError):
        BadProvider()
