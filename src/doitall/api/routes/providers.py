"""Providers route — list all registered AI providers and their status."""

from fastapi import APIRouter

from doitall.api.models import ProviderInfo, ProvidersResponse
from doitall.config.settings import settings
from doitall.services.registry import container

router = APIRouter()


@router.get(
    "/providers",
    response_model=ProvidersResponse,
    summary="List available AI providers",
    tags=["system"],
)
async def providers() -> ProvidersResponse:
    """
    Return the list of all registered AI providers with their availability.

    A provider is considered *available* if its health check passes.
    The default provider is determined by the DEFAULT_PROVIDER setting.
    """
    manager = container.resolve("provider_manager")
    all_providers = manager.all()
    default_name = settings.DEFAULT_PROVIDER

    result: list[ProviderInfo] = []

    for provider in all_providers:
        try:
            available = await provider.health_check()
        except Exception:
            available = False

        result.append(
            ProviderInfo(
                name=provider.name,
                default=provider.name == default_name,
                available=available,
            )
        )

    return ProvidersResponse(providers=result)
