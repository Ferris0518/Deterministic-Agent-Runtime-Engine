"""MCP protocol client interfaces."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from dare_framework3._internal.tool.types import RunContext, ToolDefinition, ToolResult


@runtime_checkable
class IMCPClient(Protocol):
    """Minimal MCP client interface for discovering and invoking remote tools."""

    @property
    def name(self) -> str:
        ...

    @property
    def transport(self) -> str:
        ...

    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    async def list_tools(self) -> list[ToolDefinition]:
        ...

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: RunContext[Any],
    ) -> ToolResult:
        ...
