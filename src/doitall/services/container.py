from typing import Any


class ServiceContainer:
    """Simple dependency injection container."""

    def __init__(self) -> None:
        self._services_by_name: dict[str, Any] = {}
        self._services_by_type: dict[type[Any], Any] = {}

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        """Register a singleton service."""

        self._services_by_name[name] = service
        self._services_by_type[type(service)] = service

    def resolve(
        self,
        name: str,
    ) -> Any:
        """Resolve a service by name."""

        if name not in self._services_by_name:
            raise KeyError(f"Service '{name}' is not registered.")

        return self._services_by_name[name]

    def resolve_type(
        self,
        service_type: type[Any],
    ) -> Any:
        if service_type not in self._services_by_type:
            raise KeyError(f"Service '{service_type.__name__}' is not registered.")

        return self._services_by_type[service_type]

    def has(
        self,
        name: str,
    ) -> bool:
        return name in self._services_by_name

    def has_type(
        self,
        service_type: type[Any],
    ) -> bool:
        return service_type in self._services_by_type

    def remove(
        self,
        name: str,
    ) -> None:
        service = self._services_by_name.pop(name, None)

        if service is not None:
            self._services_by_type.pop(type(service), None)

    def clear(self) -> None:
        self._services_by_name.clear()
        self._services_by_type.clear()
