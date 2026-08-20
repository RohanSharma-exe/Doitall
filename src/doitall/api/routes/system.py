"""System capability, extension, and token management endpoints."""

import asyncio
import threading
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from doitall.config.settings import settings
from doitall.security.auth import require_api_key
from doitall.services.registry import container

router = APIRouter(dependencies=[Depends(require_api_key)])

ExtensionKind = Literal["connector", "mcp_server", "plugin"]

# BUG-N006: Protect _extension_options from concurrent mutations.
_extension_lock = threading.Lock()
# BUG-N001: Extension registrations are in-memory only and are lost on restart.
# This is intentional for the current milestone; persistent storage is tracked
# as a Milestone 2 item.  Clients should treat POST /v1/extensions as ephemeral.
_extension_options: dict[ExtensionKind, list[dict[str, str]]] = {
    "connector": [],
    "mcp_server": [],
    "plugin": [],
}

# BUG-N010: MCP server and plugin kinds are currently stubs with no backend
# implementation.  Registrations via POST /v1/extensions for these kinds return
# 501 until real support lands.
_STUB_EXTENSION_KINDS: frozenset[ExtensionKind] = frozenset({"mcp_server", "plugin"})


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


_DEFAULT_MODELS: dict[str, str | None] = {
    "openai": settings.OPENAI_MODEL,
    "gemini": settings.GEMINI_MODEL,
    "groq": settings.GROQ_MODEL,
    "anthropic": settings.ANTHROPIC_MODEL,
    "openrouter": settings.OPENROUTER_MODEL,
    "ollama": settings.OLLAMA_MODEL,
    "nvidia": settings.NVIDIA_MODEL,
}

# ---------------------------------------------------------------------------
# BUG-N004: Token estimation helpers
# ---------------------------------------------------------------------------

# Mapping of tiktoken encoding name → provider model prefixes that use it.
_TIKTOKEN_ENCODING_PREFIXES: list[tuple[str, list[str]]] = [
    ("cl100k_base", ["gpt-4", "gpt-3.5", "text-embedding-ada", "claude"]),
    ("o200k_base", ["gpt-4o", "o1", "o3"]),
]


def _estimate_tokens(text: str, model: str | None = None) -> tuple[int, str]:
    """Return (token_count, method_label) for *text*.

    Uses tiktoken when the model maps to a known encoding family.
    Falls back to the 4-chars/token heuristic for unknown models.
    """
    if model:
        encoding_name: str | None = None
        model_lower = model.lower()
        for enc, prefixes in _TIKTOKEN_ENCODING_PREFIXES:
            if any(model_lower.startswith(p) for p in prefixes):
                encoding_name = enc
                break

        if encoding_name:
            try:
                import tiktoken

                enc = tiktoken.get_encoding(encoding_name)
                return len(enc.encode(text)), f"tiktoken:{encoding_name}"
            except Exception:
                pass  # Fall through to heuristic

    return max(1, (len(text) + 3) // 4), "chars_per_token_4"


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------


@router.get("/models", response_model=ModelsResponse, tags=["system"])
async def list_models() -> ModelsResponse:
    """Return selectable model defaults for every registered provider."""
    manager = container.resolve("provider_manager")
    default_provider = settings.DEFAULT_PROVIDER

    # BUG-N005: Fetch available models from all providers in parallel.
    providers = manager.all()

    async def _fetch(provider):  # type: ignore[no-untyped-def]
        discovered = await provider.available_models()
        configured_model = _DEFAULT_MODELS.get(provider.name)
        names = discovered or ([configured_model] if configured_model else [])
        return [
            ModelOption(
                provider=provider.name,
                model=name,
                default=provider.name == default_provider and name == configured_model,
            )
            for name in names
        ]

    results = await asyncio.gather(*[_fetch(p) for p in providers])
    models: list[ModelOption] = [m for batch in results for m in batch]
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
    with _extension_lock:
        configured = [
            ExtensionOption(kind=kind, status="configured", **option)
            for kind, options in _extension_options.items()
            for option in options
        ]
    return ExtensionsResponse(extensions=builtins + configured)


@router.post("/extensions", response_model=ExtensionOption, tags=["system"])
def add_extension(request: ExtensionRequest) -> ExtensionOption:
    """Store extension metadata so clients can expose add/configure flows.

    Note: registrations are held in process memory and are lost on restart.
    MCP server and plugin kinds are not yet implemented; registration returns
    501 until a real backend is added.
    """
    # BUG-N010: mcp_server and plugin kinds have no backend implementation.
    if request.kind in _STUB_EXTENSION_KINDS:
        raise HTTPException(
            status_code=501,
            detail=(
                f"Extension kind '{request.kind}' is not yet implemented. "
                "MCP server and plugin support is planned for a future release."
            ),
        )

    with _extension_lock:
        options = _extension_options[request.kind]
        if any(option["name"] == request.name for option in options):
            raise HTTPException(status_code=409, detail="Extension already configured")
        option = {"name": request.name, "description": request.description}
        options.append(option)

    return ExtensionOption(kind=request.kind, status="configured", **option)


@router.post("/tokens/estimate", response_model=TokenEstimateResponse, tags=["system"])
def estimate_tokens(request: TokenEstimateRequest) -> TokenEstimateResponse:
    """Estimate token usage for prompt budgeting before a chat request."""
    count, method = _estimate_tokens(request.text, request.model)
    return TokenEstimateResponse(
        model=request.model,
        estimated_tokens=count,
        method=method,
    )
