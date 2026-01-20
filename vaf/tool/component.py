"""Tool domain component interfaces.

VAF simplified version - only essential interfaces retained.
"""

from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable

from vaf.tool.types import ToolResult, ToolDefinition


# =============================================================================
# Tool Interface
# =============================================================================

@runtime_checkable
class ITool(Protocol):
    """Executable tool contract.
    
    Tools are capability implementations that can be invoked by agents.
    """

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description."""
        ...

    @property
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema for input validation."""
        ...

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """Execute the tool.
        
        Args:
            params: Tool input parameters
            
        Returns:
            Tool execution result
        """
        ...
    
    def get_definition(self) -> ToolDefinition:
        """Get tool definition for model function calling."""
        ...


# =============================================================================
# Tool Gateway Interface
# =============================================================================

class IToolGateway(Protocol):
    """Tool invocation gateway.
    
    Manages tool registration and invocation.
    """

    def register_tool(self, tool: ITool) -> None:
        """Register a tool.
        
        Args:
            tool: The tool to register
        """
        ...
    
    def get_tool(self, name: str) -> ITool | None:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            The tool if found, None otherwise
        """
        ...

    def list_tools(self) -> Sequence[ITool]:
        """List all registered tools.
        
        Returns:
            Sequence of registered tools
        """
        ...
    
    def get_definitions(self) -> list[ToolDefinition]:
        """Get all tool definitions for model function calling.
        
        Returns:
            List of tool definitions
        """
        ...

    async def invoke(self, tool_name: str, params: dict[str, Any]) -> ToolResult:
        """Invoke a tool by name.
        
        Args:
            tool_name: Name of the tool to invoke
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        ...
