from __future__ import annotations

from typing import Any, Iterable, Protocol, runtime_checkable

from .models.config import Config
from .composition import IComponent, IConfigurableComponent


@runtime_checkable
class IConfigProvider(IComponent, Protocol):
    """Provides resolved configuration and supports reload (Interface_Layer_Design_v1.1)."""

    def current(self) -> Config:
        """Return the current effective configuration."""
        ...

    def reload(self) -> Config:
        """Reload configuration and return the effective result."""
        ...


@runtime_checkable
class IPromptStore(IConfigurableComponent, Protocol):
    """Stores prompts by name/version (Interface_Layer_Design_v1.1)."""

    def get_prompt(self, name: str, version: str | None = None) -> str:
        """Retrieve a prompt string by name and optional version."""
        ...


def merge_config_layers(layers: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Merge layered config dictionaries using deterministic override semantics."""
    merged: dict[str, Any] = {}
    for layer in layers:
        merged = _deep_merge(merged, layer)
    return merged


def build_config_from_layers(layers: Iterable[dict[str, Any]]) -> Config:
    """Build an effective Config from layered dictionaries."""
    return Config.from_dict(merge_config_layers(layers))


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
