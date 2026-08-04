"""Provider-specific exception classes."""


class ProviderError(Exception):
    """Base provider exception."""


class ProviderAuthenticationError(ProviderError):
    """Raised when authentication with LLM provider API fails."""


class ProviderRateLimitError(ProviderError):
    """Raised when LLM provider rate limit is exceeded."""


class ProviderUnavailableError(ProviderError):
    """Raised when LLM provider service is temporarily unavailable."""


class ProviderTimeoutError(ProviderError):
    """Raised when LLM provider call times out."""


class ProviderResponseError(ProviderError):
    """Raised when invalid or unparseable response is returned by LLM provider."""
