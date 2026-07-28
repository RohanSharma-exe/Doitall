from doitall.core.bootstrap import bootstrap


class Application:
    """Main application object."""

    def start(self) -> None:
        bootstrap()

    def stop(self) -> None:
        pass
