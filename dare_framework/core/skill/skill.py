from __future__ import annotations

from typing import runtime_checkable, Protocol, Any

from dare_framework.core.configurable_component import IConfigurableComponent
from dare_framework.core.context.models import RunContext
from dare_framework.core.tool.models import ToolResult


@runtime_checkable
class ISkill(IConfigurableComponent, Protocol):
    """Plan-time skill contract (Interface_Layer_Design_v1.1)."""

    @property
    def name(self) -> str:
        """Unique skill identifier."""
        ...

    async def execute(self, input: dict[str, Any], context: RunContext) -> ToolResult:
        """Execute the skill within a run context."""
        ...
