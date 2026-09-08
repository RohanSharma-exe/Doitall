from doitall.config.settings import settings
from doitall.providers.litellm_provider import LiteLLMProvider
from doitall.providers.manager import ProviderManager


def _make_gemini() -> LiteLLMProvider:
    return LiteLLMProvider("gemini", settings.GEMINI_MODEL)


def test_register_provider():
    manager = ProviderManager()
    manager.register(_make_gemini(), default=True)

    assert manager.exists("gemini")
    assert manager.default().name == "gemini"


def test_provider_names():
    manager = ProviderManager()
    manager.register(_make_gemini(), default=True)

    assert "gemini" in manager.names()


def test_provider_all_returns_registered_providers():
    manager = ProviderManager()
    manager.register(_make_gemini(), default=True)

    providers = manager.all()

    assert [p.name for p in providers] == ["gemini"]


def test_set_default_provider():
    manager = ProviderManager()
    manager.register(_make_gemini(), default=True)
    manager.set_default("gemini")

    assert manager.default().name == "gemini"
