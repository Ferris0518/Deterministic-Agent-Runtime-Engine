from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from dare_framework.core.mcp.mcp import Resource, ResourceContent
from dare_framework.core.context.models import RunContext
from dare_framework.core.tool.models import ToolDefinition, ToolResult
from dare_framework.core.configurable_component import IConfigurableComponent


@runtime_checkable
class IMCPClient(IConfigurableComponent, Protocol):
    """MCP client interface for remote tool/resource access (Interface_Layer_Design_v1.1)."""

    @property
    def name(self) -> str:
        """Unique MCP client identifier."""
        ...

    @property
    def transport(self) -> str:
        """Transport type (stdio, sse, websocket)."""
        ...

    async def connect(self) -> None:
        """Connect to the MCP server."""
        ...

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        ...

    async def list_tools(self) -> list[ToolDefinition]:
        """List tools exposed by the MCP server."""
        ...

    async def call_tool(self, tool_name: str, arguments: dict[str, Any], context: RunContext) -> ToolResult:
        """Invoke a tool on the MCP server."""
        ...

    async def list_resources(self) -> list[Resource]:
        """List resources exposed by the MCP server."""
        ...

    async def read_resource(self, uri: str) -> ResourceContent:
        """Read a resource from the MCP server."""
        ...
