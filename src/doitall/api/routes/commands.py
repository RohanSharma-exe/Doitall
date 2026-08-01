"""Slash command discovery endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from doitall.commands import Command, default_registry
from doitall.security.auth import require_api_key

router = APIRouter()
_registry = default_registry()


class CommandsResponse(BaseModel):
    commands: list[Command]


@router.get(
    "/commands",
    response_model=CommandsResponse,
    summary="List available slash commands",
    tags=["commands"],
    dependencies=[Depends(require_api_key)],
)
def list_commands(include_hidden: bool = False) -> CommandsResponse:
    """Return command metadata for building a searchable command palette."""
    return CommandsResponse(commands=_registry.list(include_hidden=include_hidden))
