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


def test_provider_all_returns_registered_providers():
    manager = ProviderManager()

    manager.register(
        GeminiProvider(),
        default=True,
    )

    providers = manager.all()

    assert [provider.name for provider in providers] == ["gemini"]


def test_set_default_provider():
    manager = ProviderManager()

    manager.register(
        GeminiProvider(),
        default=True,
    )
    manager.set_default("gemini")

    assert manager.default().name == "gemini"
