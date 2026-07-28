from doitall.providers.factory import ProviderFactory
from doitall.providers.gemini import GeminiProvider
from doitall.providers.manager import ProviderManager


def test_factory_returns_default_provider():
    manager = ProviderManager()

    manager.register(
        GeminiProvider(),
        default=True,
    )

    factory = ProviderFactory(manager)

    provider = factory.get()

    assert provider.name == "gemini"
