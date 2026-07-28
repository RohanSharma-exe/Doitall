from doitall.config.settings import settings
from doitall.providers.manager import ProviderManager


class ProviderFactory:
    """Returns the configured default provider."""

    def __init__(self, manager: ProviderManager):
        self.manager = manager

    def get(self):
        default_provider = getattr(settings, "DEFAULT_PROVIDER", None)

        if default_provider and self.manager.exists(default_provider):
            return self.manager.get(default_provider)

        return self.manager.default()
