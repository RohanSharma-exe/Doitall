from doitall.providers.manager import ProviderManager


class Provider:
    def __init__(self, name: str) -> None:
        self.name = name


def test_fallback_candidates_default_first_then_sorted_rest():
    manager = ProviderManager()
    manager.register(Provider("b"), default=True)
    manager.register(Provider("a"))
    manager.register(Provider("c"))

    candidates = manager.fallback_candidates()

    assert [candidate.provider.name for candidate in candidates] == ["b", "a", "c"]
    assert candidates[0].is_default is True


def test_fallback_candidates_preferred_first():
    manager = ProviderManager()
    manager.register(Provider("b"), default=True)
    manager.register(Provider("a"))

    candidates = manager.fallback_candidates("a")

    assert [candidate.provider.name for candidate in candidates] == ["a", "b"]
    assert candidates[1].is_default is True
