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


RETRYABLE_PROVIDER_ERRORS = (
    ProviderRateLimitError,
    ProviderUnavailableError,
    ProviderTimeoutError,
)


def is_retryable_provider_error(error: Exception) -> bool:
    """Return whether a provider failure is safe to retry on another provider."""
    return isinstance(error, RETRYABLE_PROVIDER_ERRORS)
