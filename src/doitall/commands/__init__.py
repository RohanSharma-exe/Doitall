"""Slash command subpackage managing chat slash commands, registries, and execution handling."""

from doitall.commands.registry import Command, CommandRegistry, default_registry

__all__ = ["Command", "CommandRegistry", "default_registry"]
