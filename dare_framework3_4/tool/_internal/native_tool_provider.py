"""Native tool provider implementation.

Manages local ITool instances and exposes them as capabilities.
"""

from __future__ import annotations

from typing import Any

from dare_framework3_4.tool.interfaces import ICapabilityProvider, ITool, RunContext
from dare_framework3_4.tool.types import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityMetadata,
    CapabilityType,
    ProviderStatus,
    ToolResult,
)


class NativeToolProvider(ICapabilityProvider):
    """Provider for locally registered ITool implementations.
    
    V4 alignment:
    - Converts ITool to CapabilityDescriptor (trusted metadata)
    - Supports dynamic registration/unregistration
    - Provides health check
    """

    def __init__(self) -> None:
        self._tools: dict[str, ITool] = {}
        self._run_context: RunContext[Any] = RunContext()

    def register_tool(self, tool: ITool) -> None:
        """Register a tool.
        
        Args:
            tool: The tool to register.
            
        Raises:
            ValueError: If tool with same name already registered.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool by name.
        
        Args:
            name: The tool name to unregister.
            
        Returns:
            True if tool was found and removed, False otherwise.
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get_tool(self, name: str) -> ITool | None:
        """Get a tool by name.
        
        Args:
            name: The tool name.
            
        Returns:
            The tool or None if not found.
        """
        return self._tools.get(name)

    def set_run_context(self, context: RunContext[Any]) -> None:
        """Set the run context for tool executions.
        
        Args:
            context: The run context to use.
        """
        self._run_context = context

    async def list(self) -> list[CapabilityDescriptor]:
        """List all registered tools as capabilities."""
        capabilities: list[CapabilityDescriptor] = []
        
        for tool in self._tools.values():
            metadata = CapabilityMetadata(
                risk_level=tool.risk_level,
                requires_approval=tool.requires_approval,
                timeout_seconds=tool.timeout_seconds,
                is_work_unit=tool.is_work_unit,
                capability_kind=CapabilityKind.TOOL,
            )
            
            capability = CapabilityDescriptor(
                id=tool.name,
                type=CapabilityType.TOOL,
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
                output_schema=tool.output_schema,
                metadata=metadata,
            )
            capabilities.append(capability)
        
        return capabilities

    async def invoke(self, capability_id: str, params: dict[str, Any]) -> ToolResult:
        """Invoke a tool by capability ID.
        
        Args:
            capability_id: The tool name (capability ID).
            params: Parameters to pass to the tool.
            
        Returns:
            ToolResult from the tool execution.
            
        Raises:
            KeyError: If tool not found.
        """
        tool = self._tools.get(capability_id)
        if tool is None:
            raise KeyError(f"Tool not found: {capability_id}")
        
        return await tool.execute(params, self._run_context)

    async def health_check(self) -> ProviderStatus:
        """Check provider health.
        
        Returns:
            HEALTHY if tools are registered, DEGRADED if empty.
        """
        if len(self._tools) > 0:
            return ProviderStatus.HEALTHY
        return ProviderStatus.DEGRADED

    def list_tools(self) -> list[dict[str, Any]]:
        """Get tool definitions in LLM-compatible format.
        
        Implements IToolProvider for BaseContext integration.
        """
        tool_defs: list[dict[str, Any]] = []
        
        for tool in self._tools.values():
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            tool_defs.append(tool_def)
        
        return tool_defs


__all__ = ["NativeToolProvider"]
