"""Execution domain facade (compat shim)."""

from dare_framework3.execution.kernel import (
    IRunLoop,
    ILoopOrchestrator,
    IExecutionControl,
    IResourceManager,
    IEventLog,
    IExtensionPoint,
)
from dare_framework3.execution.components import IHook
from dare_framework3.execution.types import (
    RunLoopState,
    TickResult,
    ExecutionSignal,
    Budget,
    ResourceType,
    Event,
    RuntimeSnapshot,
    HookPhase,
)

__all__ = [
    "IRunLoop",
    "ILoopOrchestrator",
    "IExecutionControl",
    "IResourceManager",
    "IEventLog",
    "IExtensionPoint",
    "IHook",
    "RunLoopState",
    "TickResult",
    "ExecutionSignal",
    "Budget",
    "ResourceType",
    "Event",
    "RuntimeSnapshot",
    "HookPhase",
]
