from doitall.knowledge.loader import DocumentLoader


class LoaderRegistry:
    def __init__(self) -> None:
        self._loaders: dict[str, DocumentLoader] = {}

    def register(
        self,
        extension: str,
        loader: DocumentLoader,
    ) -> None:
        self._loaders[extension.lower()] = loader

    def get(
        self,
        extension: str,
    ) -> DocumentLoader | None:
        return self._loaders.get(extension.lower())

    @property
    def extensions(
        self,
    ) -> set[str]:
        return set(self._loaders.keys())
