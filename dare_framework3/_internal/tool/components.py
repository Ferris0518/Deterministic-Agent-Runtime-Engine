"""Tool domain component interfaces."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from dare_framework3._internal.tool.types import CapabilityDescriptor, RiskLevel, RunContext, ToolResult, ToolType


@runtime_checkable
class ITool(Protocol):
    """Executable tool contract."""

    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def input_schema(self) -> dict[str, Any]:
        ...

    @property
    def output_schema(self) -> dict[str, Any]:
        ...

    @property
    def tool_type(self) -> ToolType:
        ...

    @property
    def risk_level(self) -> RiskLevel:
        ...

    @property
    def requires_approval(self) -> bool:
        ...

    @property
    def timeout_seconds(self) -> int:
        ...

    @property
    def produces_assertions(self) -> list[dict[str, Any]]:
        ...

    @property
    def is_work_unit(self) -> bool:
        ...

    async def execute(
        self,
        input: dict[str, Any],
        context: RunContext[Any],
    ) -> ToolResult:
        ...


@runtime_checkable
class ISkill(Protocol):
    """A pluggable skill capability."""

    @property
    def name(self) -> str:
        ...

    async def execute(
        self,
        input: dict[str, Any],
        context: RunContext[Any],
    ) -> ToolResult:
        ...


class ICapabilityProvider(Protocol):
    """Provides capabilities to the Kernel tool gateway."""

    async def list(self) -> list[CapabilityDescriptor]:
        ...

    async def invoke(
        self,
        capability_id: str,
        params: dict[str, Any],
    ) -> object:
        ...
