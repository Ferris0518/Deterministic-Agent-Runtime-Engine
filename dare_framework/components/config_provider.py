from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

from ..core.interfaces import IConfigProvider
from .base_component import BaseComponent


class StaticConfigProvider(BaseComponent, IConfigProvider):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._config.get(key, default)

    def get_namespace(self, namespace: str) -> dict[str, Any]:
        prefix = f"{namespace}." if namespace else ""
        return {
            key[len(prefix) :]: value
            for key, value in self._config.items()
            if key.startswith(prefix)
        }


class LayeredConfigProvider(BaseComponent, IConfigProvider):
    """Merge system/project/user/session configs with validation and namespaced access."""

    def __init__(
        self,
        system: dict[str, Any] | None = None,
        project: dict[str, Any] | None = None,
        user: dict[str, Any] | None = None,
        session: dict[str, Any] | None = None,
    ) -> None:
        self._layers = {
            "system": system or {},
            "project": project or {},
            "user": user or {},
            "session": session or {},
        }
        self._effective_config = self._merge_layers()
        self._validate_config(self._effective_config)
        self._hash = self._hash_config(self._effective_config)

    @property
    def config_hash(self) -> str:
        return self._hash

    @property
    def sources(self) -> list[str]:
        return [name for name, cfg in self._layers.items() if cfg]

    def get(self, key: str, default: Any | None = None) -> Any:
        if not key:
            return self._effective_config
        return _get_by_dotted_key(self._effective_config, key, default)

    def get_namespace(self, namespace: str) -> dict[str, Any]:
        if not namespace:
            return dict(self._effective_config)
        value = _get_by_dotted_key(self._effective_config, namespace, {})
        return value if isinstance(value, dict) else {}

    def _merge_layers(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for layer_name in ("system", "project", "user", "session"):
            merged = _deep_merge(merged, self._layers[layer_name])
        return merged

    def _validate_config(self, config: dict[str, Any]) -> None:
        allowed_keys = {
            "llm",
            "mcp",
            "tools",
            "skills",
            "validators",
            "hooks",
            "allow",
            "deny",
            "composite_tools",
            "runtime",
        }
        for key, value in config.items():
            if key not in allowed_keys:
                raise ValueError(f"Unknown config key: {key}")
            if key == "composite_tools" and not isinstance(value, (list, dict)):
                raise ValueError("composite_tools must be a list or dict")
            if key in {"allow", "deny"} and not isinstance(value, (list, dict)):
                raise ValueError(f"{key} must be a list or dict")
            if key not in {"composite_tools", "allow", "deny"} and not isinstance(value, dict):
                raise ValueError(f"{key} must be a dict")

    def _hash_config(self, config: dict[str, Any]) -> str:
        payload = json.dumps(config, sort_keys=True)
        return sha256(payload.encode("utf-8")).hexdigest()


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _get_by_dotted_key(config: dict[str, Any], dotted: str, default: Any) -> Any:
    current: Any = config
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current
