"""Tool domain facade (compat shim)."""

from dare_framework3.tool.kernel import IToolGateway
from dare_framework3.tool.components import ITool, ICapabilityProvider, ISkill
from dare_framework3.tool.types import (
    RiskLevel,
    ToolType,
    CapabilityType,
    Evidence,
    ToolDefinition,
    ToolResult,
    ToolErrorRecord,
    CapabilityDescriptor,
    RunContext,
)

__all__ = [
    "IToolGateway",
    "ITool",
    "ICapabilityProvider",
    "ISkill",
    "RiskLevel",
    "ToolType",
    "CapabilityType",
    "Evidence",
    "ToolDefinition",
    "ToolResult",
    "ToolErrorRecord",
    "CapabilityDescriptor",
    "RunContext",
]
