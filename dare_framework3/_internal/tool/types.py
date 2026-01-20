"""Tool domain data types."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar


class RiskLevel(Enum):
    """Risk level classification for capabilities that may have side effects."""

    READ_ONLY = "read_only"
    IDEMPOTENT_WRITE = "idempotent_write"
    COMPENSATABLE = "compensatable"
    NON_IDEMPOTENT_EFFECT = "non_idempotent_effect"


class ToolType(Enum):
    """Tool classification used by model adapters and validators."""

    ATOMIC = "atomic"
    WORKUNIT = "workunit"


class CapabilityType(Enum):
    """Canonical capability types."""

    TOOL = "tool"
    AGENT = "agent"
    UI = "ui"


@dataclass
class Evidence:
    """Evidence record suitable for auditing and verification."""

    evidence_id: str
    kind: str
    payload: Any
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ToolDefinition:
    """Trusted tool metadata exposed to planners/models."""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    tool_type: ToolType = ToolType.ATOMIC
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    requires_approval: bool = False
    timeout_seconds: int = 30
    produces_assertions: list[dict[str, Any]] = field(default_factory=list)
    is_work_unit: bool = False


@dataclass(frozen=True)
class ToolResult:
    """Canonical tool invocation result, including evidence."""

    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class ToolErrorRecord:
    """Structured tool error record for remediation."""

    error_type: str
    tool_name: str
    message: str
    user_hint: str | None = None


@dataclass(frozen=True)
class CapabilityDescriptor:
    """Canonical description of an invokable capability."""

    id: str
    type: CapabilityType
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


DepsT = TypeVar("DepsT")


@dataclass
class RunContext(Generic[DepsT]):
    """Minimal tool execution context."""

    deps: DepsT | None
    run_id: str
    task_id: str | None = None
    milestone_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    config: Any | None = None
