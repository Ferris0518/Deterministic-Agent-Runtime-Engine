from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, Optional, TypeVar
from uuid import uuid4

OutputT = TypeVar("OutputT")


class RuntimeState(Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CANCELLED = "cancelled"


class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVE_REQUIRED = "approve_required"


class ToolRiskLevel(Enum):
    READ_ONLY = "read_only"
    IDEMPOTENT_WRITE = "idempotent_write"
    NON_IDEMPOTENT_EFFECT = "non_idempotent_effect"
    COMPENSATABLE = "compensatable"


@dataclass(frozen=True)
class VerificationSpec:
    type: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Expectation:
    description: str
    priority: str = "MUST"
    verification_spec: Optional[VerificationSpec] = None


@dataclass
class Task:
    description: str
    task_id: str = field(default_factory=lambda: uuid4().hex)
    milestones: list["Milestone"] | None = None
    expectations: list[Expectation] = field(default_factory=list)

    def to_milestones(self) -> list["Milestone"]:
        if self.milestones:
            return self.milestones
        return [
            Milestone(
                milestone_id=uuid4().hex,
                description=self.description,
                expectations=self.expectations,
            )
        ]


@dataclass
class Milestone:
    milestone_id: str
    description: str
    expectations: list[Expectation] = field(default_factory=list)


@dataclass(frozen=True)
class PlanBudget:
    max_attempts: int = 3


@dataclass(frozen=True)
class ToolBudget:
    max_iterations: int = 3


@dataclass(frozen=True)
class DonePredicate:
    required_keys: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass(frozen=True)
class Envelope:
    allowed_tools: list[str] = field(default_factory=list)
    budget: ToolBudget = field(default_factory=ToolBudget)
    done_predicate: DonePredicate | None = None


@dataclass(frozen=True)
class PlanStep:
    tool_name: str
    tool_input: dict[str, Any]
    step_id: str = field(default_factory=lambda: uuid4().hex)
    envelope: Envelope | None = None


@dataclass(frozen=True)
class ProposedPlan:
    steps: list[PlanStep]
    summary: str | None = None
    attempt: int = 0


@dataclass(frozen=True)
class ValidatedPlan:
    steps: list[PlanStep]
    summary: str | None = None
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ValidationResult:
    success: bool
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VerifyResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    risk_level: ToolRiskLevel = ToolRiskLevel.READ_ONLY
    requires_approval: bool = False
    timeout_seconds: int = 30
    produces_assertions: list[dict[str, Any]] = field(default_factory=list)
    is_work_unit: bool = False


@dataclass(frozen=True)
class ToolResult:
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecuteResult:
    success: bool
    outputs: list[ToolResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    encountered_plan_tool: bool = False
    plan_tool_name: str | None = None


@dataclass(frozen=True)
class MilestoneResult:
    success: bool
    outputs: list[ToolResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    verify_result: VerifyResult | None = None


@dataclass(frozen=True)
class RunResult(Generic[OutputT]):
    success: bool
    output: OutputT | None = None
    milestone_results: list[MilestoneResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Event:
    event_type: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    prev_hash: str | None = None
    event_hash: str | None = None


@dataclass(frozen=True)
class EventFilter:
    event_type: str | None = None
    milestone_id: str | None = None
    checkpoint_id: str | None = None
    run_id: str | None = None


@dataclass
class RunContext:
    run_id: str
    task_id: str
    milestone_id: str
    reflections: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class ModelResponse:
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class RuntimeSnapshot:
    state: RuntimeState
    task_id: str
    milestone_id: str | None
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
