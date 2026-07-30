"""Dependency injection container for managing application services."""

from typing import Any


class ServiceContainer:
    """Simple dependency injection container for managing singleton services.

    The container allows registration and resolution of services by both name
    and type, supporting constructor injection patterns throughout the application.
    """

    def __init__(self) -> None:
        self._services_by_name: dict[str, Any] = {}
        self._services_by_type: dict[type[Any], Any] = {}

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        """Register a singleton service.

        Args:
            name: The name to register the service under.
            service: The service instance to register.
        """
        self._services_by_name[name] = service
        self._services_by_type[type(service)] = service

    def resolve(
        self,
        name: str,
    ) -> Any:
        """Resolve a service by name.

        Args:
            name: The name of the service to resolve.

        Returns:
            The registered service instance.

        Raises:
            KeyError: If the service is not registered.
        """
        if name not in self._services_by_name:
            raise KeyError(f"Service '{name}' is not registered.")

        return self._services_by_name[name]

    def resolve_type(
        self,
        service_type: type[Any],
    ) -> Any:
        """Resolve a service by type.

        Args:
            service_type: The type of the service to resolve.

        Returns:
            The registered service instance.

        Raises:
            KeyError: If the service is not registered.
        """
        if service_type not in self._services_by_type:
            raise KeyError(f"Service '{service_type.__name__}' is not registered.")

        return self._services_by_type[service_type]

    def has(
        self,
        name: str,
    ) -> bool:
        """Check if a service is registered by name.

        Args:
            name: The name to check.

        Returns:
            True if the service is registered, False otherwise.
        """
        return name in self._services_by_name

    def has_type(
        self,
        service_type: type[Any],
    ) -> bool:
        """Check if a service is registered by type.

        Args:
            service_type: The type to check.

        Returns:
            True if the service is registered, False otherwise.
        """
        return service_type in self._services_by_type

    def remove(
        self,
        name: str,
    ) -> None:
        """Remove a service from the container.

        Args:
            name: The name of the service to remove.
        """
        service = self._services_by_name.pop(name, None)

        if service is not None:
            self._services_by_type.pop(type(service), None)

    def clear(self) -> None:
        """Clear all services from the container."""
        self._services_by_name.clear()
        self._services_by_type.clear()
