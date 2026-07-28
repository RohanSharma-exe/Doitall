class ProviderError(Exception):
    """Base provider exception."""


class ProviderAuthenticationError(ProviderError):
    """Authentication failed."""


class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded."""


class ProviderUnavailableError(ProviderError):
    """Provider unavailable."""


class ProviderTimeoutError(ProviderError):
    """Provider timeout."""


class ProviderResponseError(ProviderError):
    """Invalid provider response."""
