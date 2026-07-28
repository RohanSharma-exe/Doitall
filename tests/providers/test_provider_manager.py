from doitall.providers.gemini import GeminiProvider
from doitall.providers.manager import ProviderManager


def test_register_provider():
    manager = ProviderManager()

    manager.register(
        GeminiProvider(),
        default=True,
    )

    assert manager.exists("gemini")
    assert manager.default().name == "gemini"


def test_provider_names():
    manager = ProviderManager()

    manager.register(
        GeminiProvider(),
        default=True,
    )

    assert "gemini" in manager.names()
