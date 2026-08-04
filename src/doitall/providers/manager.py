"""LLM provider registry and failover management module."""

from dataclasses import dataclass

from doitall.providers.base import BaseProvider


@dataclass(frozen=True)
class ProviderCandidate:
    """Dataclass holding candidate provider and default status for failover ordering."""

    provider: BaseProvider
    is_default: bool = False


class ProviderManager:
    """Central registry and failover manager for AI providers."""

    def __init__(self) -> None:
        """Initialize empty provider map and default selection."""
        self._providers: dict[str, BaseProvider] = {}
        self._default: str | None = None

    def register(self, provider: BaseProvider, *, default: bool = False) -> None:
        """Register a provider instance and optionally mark as default."""
        self._providers[provider.name] = provider

        if default or self._default is None:
            self._default = provider.name

    def unregister(self, name: str) -> None:
        """Remove a provider by name from the registry."""
        self._providers.pop(name, None)

        if self._default == name:
            self._default = next(iter(self._providers), None)

    def get(self, name: str) -> BaseProvider:
        """Retrieve registered provider instance by name."""
        return self._providers[name]

    def set_default(self, name: str) -> None:
        """Set the default provider identifier."""
        if name not in self._providers:
            raise RuntimeError(f"Unknown provider configured as default: {name}")

        self._default = name

    def default(self) -> BaseProvider:
        """Return the current default provider instance."""
        if self._default is None:
            raise RuntimeError("No default provider configured.")

        return self._providers[self._default]

    def exists(self, name: str) -> bool:
        """Return True if a provider with given name is registered."""
        return name in self._providers

    def names(self) -> list[str]:
        """Return sorted list of all registered provider names."""
        return sorted(self._providers.keys())

    def all(self) -> list[BaseProvider]:
        """Return list of all registered provider instances."""
        return [self._providers[name] for name in self.names()]

    def fallback_candidates(
        self, preferred: str | None = None
    ) -> list[ProviderCandidate]:
        """Return providers ordered for failover: preferred/default first, then others."""

        ordered_names: list[str] = []
        first = preferred or self._default
        if first and first in self._providers:
            ordered_names.append(first)

        for name in self.names():
            if name not in ordered_names:
                ordered_names.append(name)

        return [
            ProviderCandidate(
                provider=self._providers[name],
                is_default=name == self._default,
            )
            for name in ordered_names
        ]

    def clear(self) -> None:
        """Clear all registered providers and reset default selection."""
        self._providers.clear()
        self._default = None

