from __future__ import annotations

# Legacy compatibility shim. Prefer `dare_framework.core.interfaces` for Layer 1
# and `dare_framework.components.layer2` for Layer 2.

from dare_framework.core.interfaces import (
    IContextAssembler,
    IEventLog,
    IPlanGenerator,
    IPolicyEngine,
    IRemediator,
    IRuntime,
    ISkillRegistry,
    IToolRuntime,
    IValidator,
    PolicyDecision,
)
from dare_framework.components.layer2 import (
    ICheckpoint,
    IHook,
    IMCPClient,
    IMemory,
    IModelAdapter,
    ISkill,
    IStreamedResponse,
    ITool,
    IToolkit,
)

__all__ = [
    "IContextAssembler",
    "IEventLog",
    "IPlanGenerator",
    "IPolicyEngine",
    "IRemediator",
    "IRuntime",
    "ISkillRegistry",
    "IToolRuntime",
    "IValidator",
    "PolicyDecision",
    "ICheckpoint",
    "IHook",
    "IMCPClient",
    "IMemory",
    "IModelAdapter",
    "ISkill",
    "IStreamedResponse",
    "ITool",
    "IToolkit",
]
