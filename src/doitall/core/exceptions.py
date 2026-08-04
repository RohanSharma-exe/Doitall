"""Custom exception hierarchy for Doitall.

Defines the domain-specific exception types raised across core, providers, plugins,
skills, embeddings, database, and authentication layers.
"""


class DoitallError(Exception):
    """Base exception for all Doitall errors."""


class ConfigurationError(DoitallError):
    """Raised when configuration values or environment setups are invalid."""


class ProviderError(DoitallError):
    """Raised when an LLM provider request fails or returns an error."""


class PluginError(DoitallError):
    """Raised when a plugin initialization or execution fails."""


class SkillError(DoitallError):
    """Raised when a skill execution or registration fails."""


class AuthenticationError(DoitallError):
    """Raised for authentication failures or invalid API key credentials."""


class AuthorizationError(DoitallError):
    """Raised for permission or access control failures."""


class ValidationError(DoitallError):
    """Raised for payload, schema, or input data validation failures."""


class EmbeddingError(DoitallError):
    """Raised when embedding generation fails."""
