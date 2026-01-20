"""Execution kernel interfaces (compat shim)."""

from dare_framework3._internal.execution.kernel import (
    IRunLoop,
    ILoopOrchestrator,
    IExecutionControl,
    IResourceManager,
    IEventLog,
    IExtensionPoint,
)

__all__ = [
    "IRunLoop",
    "ILoopOrchestrator",
    "IExecutionControl",
    "IResourceManager",
    "IEventLog",
    "IExtensionPoint",
]
