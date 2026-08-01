import secrets

from fastapi import Header, HTTPException, status

from doitall.config.settings import settings


def _matches_configured_api_key(candidate: str | None) -> bool:
    if not candidate or not settings.API_KEY:
        return False
    return secrets.compare_digest(candidate, settings.API_KEY)


async def require_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> None:
    """Require an API key when API_KEY is configured.

    Development installs can leave API_KEY unset to keep local usage frictionless.
    Production deployments should configure API_KEY and send either
    ``Authorization: Bearer <key>`` or ``X-API-Key: <key>``.
    """

    if not settings.API_KEY:
        return

    bearer_token = None
    if authorization and authorization.startswith("Bearer "):
        bearer_token = authorization.removeprefix("Bearer ").strip()

    if _matches_configured_api_key(x_api_key) or _matches_configured_api_key(
        bearer_token
    ):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key.",
    )


async def require_metrics_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> None:
    """Require API key for metrics when explicitly configured."""
    if not settings.METRICS_REQUIRE_API_KEY:
        return

    if not settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics authentication is not configured.",
        )

    await require_api_key(authorization=authorization, x_api_key=x_api_key)
