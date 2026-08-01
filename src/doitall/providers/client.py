from typing import Any

from litellm import (
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
    acompletion,
)

from doitall.config.settings import settings
from doitall.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class LiteLLMClient:
    """LiteLLM wrapper for unified LLM provider access."""

    async def stream(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ):
        """Stream chat completion text deltas from LiteLLM."""
        try:
            stream = await acompletion(
                model=model,
                messages=messages,
                timeout=settings.LLM_TIMEOUT_SECONDS,
                stream=True,
                **kwargs,
            )
            async for chunk in stream:
                delta = getattr(chunk.choices[0], "delta", None)
                content = getattr(delta, "content", None) if delta is not None else None
                if content:
                    yield content
        except AuthenticationError as e:
            raise ProviderAuthenticationError(str(e)) from e
        except RateLimitError as e:
            raise ProviderRateLimitError(str(e)) from e
        except ServiceUnavailableError as e:
            raise ProviderUnavailableError(str(e)) from e
        except Timeout as e:
            raise ProviderTimeoutError(str(e)) from e
        except Exception as e:
            raise ProviderResponseError(str(e)) from e

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> Any:
        """Send a chat completion request to the LLM provider.

        Args:
            model: The model identifier to use.
            messages: List of message dictionaries with role and content.
            **kwargs: Additional parameters to pass to the LLM provider.

        Returns:
            The LLM provider's response.

        Raises:
            ProviderAuthenticationError: If authentication fails.
            ProviderRateLimitError: If rate limit is exceeded.
            ProviderUnavailableError: If the provider is unavailable.
            ProviderTimeoutError: If the request times out.
            ProviderResponseError: For other provider errors.
        """
        try:
            return await acompletion(
                model=model,
                messages=messages,
                timeout=settings.LLM_TIMEOUT_SECONDS,
                **kwargs,
            )

        except AuthenticationError as e:
            raise ProviderAuthenticationError(str(e)) from e

        except RateLimitError as e:
            raise ProviderRateLimitError(str(e)) from e

        except ServiceUnavailableError as e:
            raise ProviderUnavailableError(str(e)) from e

        except Timeout as e:
            raise ProviderTimeoutError(str(e)) from e

        except Exception as e:
            raise ProviderResponseError(str(e)) from e

