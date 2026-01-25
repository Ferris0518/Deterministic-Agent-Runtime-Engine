"""tool domain facade."""

from dare_framework3_4.tool.interfaces import (
    ICapabilityProvider,
    IProtocolAdapter,
    ISkill,
    ITool,
    IToolProvider,
    RunContext,
)
from dare_framework3_4.tool.kernel import IExecutionControl, IToolGateway
from dare_framework3_4.tool.types import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityMetadata,
    CapabilityType,
    Evidence,
    ExecutionSignal,
    InvocationContext,
    ProviderStatus,
    RiskLevelName,
    ToolDefinition,
    ToolResult,
    ToolType,
)

# Internal implementations (convenience re-exports)
from dare_framework3_4.tool._internal import (
    Checkpoint,
    DefaultExecutionControl,
    DefaultToolGateway,
    EchoTool,
    NativeToolProvider,
    NoopTool,
    ProtocolAdapterProvider,
)

__all__ = [
    # Types
    "CapabilityDescriptor",
    "CapabilityKind",
    "CapabilityMetadata",
    "CapabilityType",
    "Checkpoint",
    "Evidence",
    "ExecutionSignal",
    "InvocationContext",
    "ProviderStatus",
    "RiskLevelName",
    "ToolDefinition",
    "ToolResult",
    "ToolType",
    # Kernel interfaces
    "IExecutionControl",
    "IToolGateway",
    # Pluggable interfaces
    "ICapabilityProvider",
    "IProtocolAdapter",
    "ISkill",
    "ITool",
    "IToolProvider",
    "RunContext",
    # Internal implementations
    "DefaultExecutionControl",
    "DefaultToolGateway",
    "EchoTool",
    "NativeToolProvider",
    "NoopTool",
    "ProtocolAdapterProvider",
]

