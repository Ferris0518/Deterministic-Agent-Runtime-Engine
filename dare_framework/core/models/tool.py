from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVE_REQUIRED = "approve_required"


class ToolType(Enum):
    ATOMIC = "atomic"
    WORKUNIT = "workunit"


class StepType(Enum):
    ATOMIC = "atomic"
    WORKUNIT = "workunit"


class RiskLevel(Enum):
    READ_ONLY = "read_only"
    IDEMPOTENT_WRITE = "idempotent_write"
    NON_IDEMPOTENT_EFFECT = "non_idempotent_effect"
    COMPENSATABLE = "compensatable"


ToolRiskLevel = RiskLevel


@dataclass
class ToolErrorRecord:
    error_type: str
    tool_name: str
    message: str
    user_hint: str | None = None


@dataclass
class Evidence:
    evidence_id: str
    kind: str
    payload: Any
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ToolDefinition:
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
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    evidence: list[Evidence] = field(default_factory=list)
