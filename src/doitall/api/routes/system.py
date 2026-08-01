"""System capability, extension, and token management endpoints."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from doitall.config.settings import settings
from doitall.security.auth import require_api_key
from doitall.services.registry import container

router = APIRouter(dependencies=[Depends(require_api_key)])

ExtensionKind = Literal["connector", "mcp_server", "plugin"]
_extension_options: dict[str, list[dict[str, str]]] = {
    "connector": [],
    "mcp_server": [],
    "plugin": [],
}


class ModelOption(BaseModel):
    provider: str
    model: str
    default: bool = False
    available: bool = True


class ModelsResponse(BaseModel):
    models: list[ModelOption]


class SkillInfo(BaseModel):
    name: str
    description: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    input_schema: dict = Field(default_factory=dict)


class SkillsResponse(BaseModel):
    skills: list[SkillInfo]


class ExtensionOption(BaseModel):
    kind: ExtensionKind
    name: str
    description: str = ""
    status: Literal["available", "configured"] = "available"


class ExtensionRequest(BaseModel):
    kind: ExtensionKind
    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(default="", max_length=1000)


class ExtensionsResponse(BaseModel):
    extensions: list[ExtensionOption]


class TokenEstimateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=settings.CHAT_MESSAGE_MAX_LENGTH)
    model: str | None = None


class TokenEstimateResponse(BaseModel):
    model: str | None = None
    estimated_tokens: int
    method: str = "chars_per_token_4"


_DEFAULT_MODELS = {
    "openai": settings.OPENAI_MODEL,
    "gemini": settings.GEMINI_MODEL,
    "groq": settings.GROQ_MODEL,
    "anthropic": settings.ANTHROPIC_MODEL,
    "openrouter": settings.OPENROUTER_MODEL,
    "ollama": settings.OLLAMA_MODEL,
}


def _estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


@router.get("/models", response_model=ModelsResponse, tags=["system"])
async def list_models() -> ModelsResponse:
    """Return selectable model defaults for every registered provider."""
    manager = container.resolve("provider_manager")
    default_provider = settings.DEFAULT_PROVIDER
    models: list[ModelOption] = []
    for provider in manager.all():
        configured_model = _DEFAULT_MODELS.get(provider.name)
        discovered = await provider.available_models()
        names = discovered or ([configured_model] if configured_model else [])
        for name in names:
            models.append(
                ModelOption(
                    provider=provider.name,
                    model=name,
                    default=provider.name == default_provider
                    and name == configured_model,
                )
            )
    return ModelsResponse(models=models)


@router.get("/skills", response_model=SkillsResponse, tags=["system"])
def list_skills() -> SkillsResponse:
    """Return registered executable skills for tool/skill pickers."""
    registry = container.resolve("skill_registry")
    return SkillsResponse(
        skills=[
            SkillInfo(
                name=skill.name,
                description=skill.description,
                version=skill.version,
                enabled=skill.enabled,
                input_schema=skill.definition().input_schema,
            )
            for skill in registry.all()
        ]
    )


@router.get("/extensions", response_model=ExtensionsResponse, tags=["system"])
def list_extensions() -> ExtensionsResponse:
    """Return connector, MCP server, and plugin options/configured entries."""
    builtins = [
        ExtensionOption(
            kind="connector",
            name="knowledge",
            description="Built-in RAG knowledge connector.",
            status="configured",
        ),
        ExtensionOption(
            kind="connector",
            name="memory",
            description="Built-in long-term memory connector.",
            status="configured",
        ),
        ExtensionOption(
            kind="mcp_server",
            name="custom",
            description="Register an external MCP server endpoint.",
        ),
        ExtensionOption(
            kind="plugin",
            name="custom",
            description="Register a local or remote plugin manifest.",
        ),
    ]
    configured = [
        ExtensionOption(kind=kind, status="configured", **option)
        for kind, options in _extension_options.items()
        for option in options
    ]
    return ExtensionsResponse(extensions=builtins + configured)


@router.post("/extensions", response_model=ExtensionOption, tags=["system"])
def add_extension(request: ExtensionRequest) -> ExtensionOption:
    """Store extension metadata so clients can expose add/configure flows."""
    options = _extension_options[request.kind]
    if any(option["name"] == request.name for option in options):
        raise HTTPException(status_code=409, detail="Extension already configured")
    option = {"name": request.name, "description": request.description}
    options.append(option)
    return ExtensionOption(kind=request.kind, status="configured", **option)


@router.post("/tokens/estimate", response_model=TokenEstimateResponse, tags=["system"])
def estimate_tokens(request: TokenEstimateRequest) -> TokenEstimateResponse:
    """Estimate token usage for prompt budgeting before a chat request."""
    return TokenEstimateResponse(
        model=request.model,
        estimated_tokens=_estimate_tokens(request.text),
    )
