from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from dare_framework.core.configurable_component import IConfigurableComponent
from dare_framework.core.context.models import RunContext
from dare_framework.core.plan.models import Envelope
from dare_framework.core.risk_level import RiskLevel
from dare_framework.core.tool.enums import ToolType
from dare_framework.core.tool.models import ToolDefinition, ToolResult


@runtime_checkable
class ITool(IConfigurableComponent, Protocol):
    """Executable tool contract for the tool runtime gate (Interface_Layer_Design_v1.1)."""

    @property
    def name(self) -> str:
        """Unique tool identifier used in plans."""
        ...

    @property
    def description(self) -> str:
        """Human-readable tool description for planners."""
        ...

    @property
    def input_schema(self) -> dict[str, Any]:
        """Schema for tool input validation and exposure to models."""
        ...

    @property
    def output_schema(self) -> dict[str, Any]:
        """Schema for tool output validation and evidence formatting."""
        ...

    @property
    def tool_type(self) -> ToolType:
        """Indicates whether the tool is atomic or a work unit."""
        ...

    @property
    def risk_level(self) -> RiskLevel:
        """Declared risk level (validated by TrustBoundary)."""
        ...

    @property
    def requires_approval(self) -> bool:
        """Whether tool usage requires human approval."""
        ...

    @property
    def timeout_seconds(self) -> int:
        """Execution timeout for the tool."""
        ...

    @property
    def produces_assertions(self) -> list[dict[str, Any]]:
        """Assertions or evidence emitted by the tool."""
        ...

    @property
    def is_work_unit(self) -> bool:
        """Whether the tool represents an internal tool loop."""
        ...

    async def execute(self, input: dict[str, Any], context: RunContext) -> ToolResult:
        """Execute the tool within the trusted runtime context."""
        ...


class IToolkit(Protocol):
    """Registry for tool instances available to the runtime (Interface_Layer_Design_v1.1)."""

    def register_tool(self, tool: ITool) -> None:
        """Register a tool instance for lookup."""
        ...

    def get_tool(self, name: str) -> ITool | None:
        """Retrieve a tool instance by name."""
        ...

    def list_tools(self) -> list[ToolDefinition]:
        """List trusted tool definitions for planners and validators."""
        ...


class IToolRegistry(Protocol):
    """Trusted registry of tool metadata for validation and policy checks (Architecture_Final_Review_v1.3)."""

    def get_tool_definition(self, name: str) -> ToolDefinition | None:
        """Return the trusted tool definition for a given tool name."""
        ...

    def list_tool_definitions(self) -> list[ToolDefinition]:
        """Return all trusted tool definitions."""
        ...


class IToolRuntime(Protocol):
    """Tool execution gate enforcing policy and approvals (Architecture_Final_Review_v1.3)."""

    async def invoke(
        self,
        name: str,
        input: dict[str, Any],
        ctx: RunContext,
        envelope: Envelope | None = None,
    ) -> ToolResult:
        """Invoke a tool by name with optional envelope constraints."""
        ...

    def get_tool(self, name: str) -> ITool | None:
        """Return a tool instance for inspection."""
        ...

    def list_tools(self) -> list[ToolDefinition]:
        """List trusted tool definitions available to the runtime."""
        ...

    def is_plan_tool(self, name: str) -> bool:
        """Identify whether a tool name refers to a plan tool/skill."""
        ...
