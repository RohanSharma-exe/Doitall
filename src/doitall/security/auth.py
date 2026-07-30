from fastapi import Header, HTTPException, status

from doitall.config.settings import settings


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

    if x_api_key == settings.API_KEY or bearer_token == settings.API_KEY:
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key.",
    )
