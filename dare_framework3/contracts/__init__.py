"""Contract facade (compat shim)."""

from dare_framework3.contracts.types import (
    Task,
    Milestone,
    Plan,
    Envelope,
    Budget,
    RunResult,
    ToolResult,
    ToolDefinition,
    CapabilityDescriptor,
    Message,
    ModelResponse,
)
from dare_framework3.contracts.errors import DAREError
from dare_framework3.contracts.ids import TaskId, MilestoneId, RunId, CapabilityId

__all__ = [
    "Task",
    "Milestone",
    "Plan",
    "Envelope",
    "Budget",
    "RunResult",
    "ToolResult",
    "ToolDefinition",
    "CapabilityDescriptor",
    "Message",
    "ModelResponse",
    "DAREError",
    "TaskId",
    "MilestoneId",
    "RunId",
    "CapabilityId",
]
