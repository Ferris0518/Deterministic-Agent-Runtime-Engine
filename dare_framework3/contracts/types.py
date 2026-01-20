"""Cross-domain shared types (compat shim)."""

from dare_framework3.types import Task, Milestone, Plan, Envelope, Budget, RunResult, ToolResult
from dare_framework3.tool.types import ToolDefinition, CapabilityDescriptor
from dare_framework3.model.types import Message, ModelResponse

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
]
