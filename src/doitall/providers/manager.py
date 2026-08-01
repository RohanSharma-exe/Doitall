from dataclasses import dataclass

from doitall.providers.base import BaseProvider


@dataclass(frozen=True)
class ProviderCandidate:
    provider: BaseProvider
    is_default: bool = False


class ProviderManager:
    """Central registry for AI providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}
        self._default: str | None = None

    def register(self, provider: BaseProvider, *, default: bool = False) -> None:
        self._providers[provider.name] = provider

        if default or self._default is None:
            self._default = provider.name

    def unregister(self, name: str) -> None:
        self._providers.pop(name, None)

        if self._default == name:
            self._default = next(iter(self._providers), None)

    def get(self, name: str) -> BaseProvider:
        return self._providers[name]

    def set_default(self, name: str) -> None:
        if name not in self._providers:
            raise RuntimeError(f"Unknown provider configured as default: {name}")

        self._default = name

    def default(self) -> BaseProvider:
        if self._default is None:
            raise RuntimeError("No default provider configured.")

        return self._providers[self._default]

    def exists(self, name: str) -> bool:
        return name in self._providers

    def names(self) -> list[str]:
        return sorted(self._providers.keys())

    def all(self) -> list[BaseProvider]:
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
        self._providers.clear()
        self._default = None
