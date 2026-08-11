"""Factory for retrieving default configured LLM provider instance."""

from doitall.config.settings import settings
from doitall.providers.base import BaseProvider
from doitall.providers.manager import ProviderManager


class ProviderFactory:
    """Returns the configured default provider instance from the provider manager."""

    def __init__(self, manager: ProviderManager) -> None:
        """Initialize provider factory with manager instance."""
        self.manager = manager

    def get(self) -> BaseProvider:
        """Retrieve default provider instance or fallback to manager default."""
        default_provider = getattr(settings, "DEFAULT_PROVIDER", None)

        if default_provider and self.manager.exists(default_provider):
            return self.manager.get(default_provider)

        return self.manager.default()
