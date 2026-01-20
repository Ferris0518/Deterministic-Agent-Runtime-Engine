"""Tool domain: Tool execution interfaces and implementations."""

from vaf.tool.component import ITool, IToolGateway
from vaf.tool.types import ToolResult, ToolDefinition
from vaf.tool.impl.default_tool_gateway import DefaultToolGateway
from vaf.tool.impl.run_command_tool import RunCommandTool

__all__ = [
    "ITool",
    "IToolGateway",
    "ToolResult",
    "ToolDefinition",
    "DefaultToolGateway",
    "RunCommandTool",
]
