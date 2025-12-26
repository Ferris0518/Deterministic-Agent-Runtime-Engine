from __future__ import annotations

from typing import Any, Iterable

from .models import Config


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
