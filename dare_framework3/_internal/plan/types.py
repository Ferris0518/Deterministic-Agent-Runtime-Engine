"""Plan domain data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dare_framework3._internal.tool.types import RiskLevel, ToolResult


@dataclass(frozen=True)
class Task:
    """Top-level task description."""

    description: str
    task_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Milestone:
    """A milestone within a task."""

    milestone_id: str
    task_id: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanStep:
    """Single step in a plan."""

    step_id: str
    description: str
    tool_name: str | None = None
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Plan:
    """Canonical plan representation."""

    steps: list[PlanStep]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProposedPlan:
    """Untrusted plan proposal from a planner."""

    steps: list[PlanStep]
    rationale: str | None = None


@dataclass(frozen=True)
class ValidatedPlan:
    """Validated plan with trusted fields attached."""

    plan: ProposedPlan
    valid: bool
    errors: list[str] = field(default_factory=list)
    trusted_fields: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Envelope:
    """Execution envelope for tool calls."""

    task: Task
    plan: ProposedPlan
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecuteResult:
    """Execution result for a milestone."""

    success: bool
    tool_results: list[ToolResult] = field(default_factory=list)
    output: Any | None = None
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VerifyResult:
    """Verification outcome for a milestone execution."""

    success: bool
    evidence: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    message: str | None = None


@dataclass(frozen=True)
class RunResult:
    """Final result of running a task."""

    success: bool
    output: Any | None = None
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MilestoneResult:
    """Result of executing a milestone."""

    milestone: Milestone
    success: bool
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolLoopRequest:
    """Request to invoke a tool capability."""

    capability_id: str
    params: dict[str, Any]
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    requires_approval: bool = False


@dataclass(frozen=True)
class ToolLoopResult:
    """Result of a tool loop invocation."""

    tool_result: ToolResult | None
    approved: bool
    errors: list[str] = field(default_factory=list)
