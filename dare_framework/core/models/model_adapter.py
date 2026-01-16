from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from dare_framework.core.configurable_component import IConfigurableComponent
from dare_framework.core.tool.models import ToolDefinition


@dataclass(frozen=True)
class Message:
    role: str
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class GenerateOptions:
    max_tokens: int | None = None
    temperature: float | None = None


@dataclass(frozen=True)
class ModelResponse:
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@runtime_checkable
class IModelAdapter(IConfigurableComponent, Protocol):
    """Model adapter for LLM inference (Interface_Layer_Design_v1.1)."""

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        options: GenerateOptions | None = None,
    ) -> ModelResponse:
        """Generate a response from model messages and optional tools."""
        ...

    async def generate_structured(self, messages: list[Message], output_schema: type[Any]) -> Any:
        """Generate structured output using a schema."""
        ...
