from litellm import (
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
    acompletion,
)

from doitall.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class LiteLLMClient:
    """LiteLLM wrapper."""

    async def chat(
        self,
        *,
        model: str,
        messages: list[dict],
        **kwargs,
    ):
        try:
            return await acompletion(
                model=model,
                messages=messages,
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
