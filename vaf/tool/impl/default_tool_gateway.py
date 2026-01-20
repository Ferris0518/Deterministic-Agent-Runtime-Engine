"""Default tool gateway implementation."""

from __future__ import annotations

from typing import Any, Sequence

from vaf.tool.component import IToolGateway, ITool
from vaf.tool.types import ToolResult, ToolDefinition


class DefaultToolGateway(IToolGateway):
    """Simple tool gateway that manages tool registration and invocation."""

    def __init__(self) -> None:
        self._tools: dict[str, ITool] = {}

    def register_tool(self, tool: ITool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> ITool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> Sequence[ITool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def get_definitions(self) -> list[ToolDefinition]:
        """Get all tool definitions for model function calling."""
        definitions = []
        for tool in self._tools.values():
            definitions.append(tool.get_definition())
        return definitions

    async def invoke(self, tool_name: str, params: dict[str, Any]) -> ToolResult:
        """Invoke a tool by name."""
        tool = self._tools.get(tool_name)
        if tool is None:
            return ToolResult(success=False, error=f"Tool '{tool_name}' not found")
        
        try:
            return await tool.execute(params)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
