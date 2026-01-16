from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LLMConfig:
    """Connectivity settings for LLM backends."""

    endpoint: str | None = None
    api_key: str | None = None
    model: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMConfig":
        endpoint = data.get("endpoint")
        api_key = data.get("api_key")
        model = data.get("model")
        extra = {key: value for key, value in data.items() if key not in {"endpoint", "api_key", "model"}}
        return cls(endpoint=endpoint, api_key=api_key, model=model, extra=extra)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.endpoint is not None:
            payload["endpoint"] = self.endpoint
        if self.api_key is not None:
            payload["api_key"] = self.api_key
        if self.model is not None:
            payload["model"] = self.model
        payload.update(self.extra)
        return payload
