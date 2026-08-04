"""Document loader extension registry module."""

from doitall.knowledge.loader import DocumentLoader


class LoaderRegistry:
    """Registry mapping file extension strings to DocumentLoader instances."""

    def __init__(self) -> None:
        """Initialize empty loader mapping dict."""
        self._loaders: dict[str, DocumentLoader] = {}

    def register(
        self,
        extension: str,
        loader: DocumentLoader,
    ) -> None:
        """Register a DocumentLoader for a specific file extension (e.g. '.txt')."""
        self._loaders[extension.lower()] = loader

    def get(
        self,
        extension: str,
    ) -> DocumentLoader | None:
        """Retrieve registered DocumentLoader for given file extension."""
        return self._loaders.get(extension.lower())

    @property
    def extensions(
        self,
    ) -> set[str]:
        """Return set of registered file extension strings."""
        return set(self._loaders.keys())
