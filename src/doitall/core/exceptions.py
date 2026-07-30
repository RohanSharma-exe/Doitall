class DoitallError(Exception):
    """Base exception for all Doitall errors."""


class ConfigurationError(DoitallError):
    """Raised when configuration is invalid."""


class ProviderError(DoitallError):
    """Raised when a provider fails."""


class PluginError(DoitallError):
    """Raised when a plugin fails."""


class SkillError(DoitallError):
    """Raised when a skill fails."""


class AuthenticationError(DoitallError):
    """Raised for authentication failures."""


class AuthorizationError(DoitallError):
    """Raised for authorization failures."""


class ValidationError(DoitallError):
    """Raised for validation failures."""


class EmbeddingError(DoitallError):
    """Raised when embedding generation fails."""
