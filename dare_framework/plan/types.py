"""plan domain types (task/plan/result/envelope)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dare_framework.context.types import Budget
from dare_framework.security.types import RiskLevel


@dataclass(frozen=True)
class Milestone:
    """A milestone representing a sub-goal within a task.

    Milestones are the unit of verification in the five-layer loop.
    Each milestone goes through its own Plan → Execute → Verify cycle.

    Attributes:
        milestone_id: Unique identifier for this milestone.
        description: What this milestone aims to achieve.
        user_input: Original user input that led to this milestone.
        success_criteria: List of criteria to verify milestone completion.

    Example:
        milestone = Milestone(
            milestone_id="m1",
            description="Implement authentication module",
            success_criteria=["All tests pass", "Code review approved"],
        )
    """

    milestone_id: str
    description: str
    user_input: str | None = None
    success_criteria: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Task:
    """A high-level execution request.

    Task is the top-level input to `IAgent.run()`. It can be used in two ways:

    1. **Simple Mode**: Just provide `description`, milestones will be auto-generated.
    2. **Orchestrated Mode**: Pre-define `milestones` for explicit multi-step execution.

    When to use milestones:
        - Complex tasks requiring multiple distinct phases (design → implement → test)
        - Tasks with specific verification checkpoints
        - Enterprise workflows with audit requirements

    When NOT to use milestones:
        - Simple questions or explanations
        - Single-step operations
        - Exploratory tasks

    Attributes:
        description: Main task description or goal.
        task_id: Optional unique identifier (auto-generated if not provided).
        milestones: Pre-defined sub-goals. If empty, a single milestone is auto-created.
        metadata: Arbitrary key-value data for context or audit.
        previous_session_summary: Optional summary from a prior session for continuity.
        resume_from_checkpoint: Reserved field for future resume workflows.

    See Also:
        doc/用户旅程地图：全栈智能研发 Agent 交付云服务 LandingZone 对接.md
    """

    description: str
    task_id: str | None = None
    milestones: list[Milestone] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    previous_session_summary: "SessionSummary | None" = None
    resume_from_checkpoint: str | None = None

    def to_milestones(self) -> list[Milestone]:
        """Convert task to a list of milestones.

        If milestones are already defined, return them.
        Otherwise, create a single milestone from the task description.
        """
        if self.milestones:
            return list(self.milestones)
        from uuid import uuid4
        return [
            Milestone(
                milestone_id=f"{self.task_id or uuid4().hex[:8]}_m1",
                description=self.description,
                user_input=self.description,
            )
        ]


@dataclass(frozen=True)
class MilestoneSummary:
    """Deterministic summary of a milestone execution."""

    milestone_id: str
    description: str
    attempts: int
    success: bool
    outputs: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    evidence_count: int = 0
    reflections_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "milestone_id": self.milestone_id,
            "description": self.description,
            "attempts": self.attempts,
            "success": self.success,
            "outputs": list(self.outputs),
            "errors": list(self.errors),
            "evidence_count": self.evidence_count,
            "reflections_count": self.reflections_count,
        }


@dataclass(frozen=True)
class SessionSummary:
    """Deterministic session summary for audit and handoff."""

    session_id: str
    task_id: str
    success: bool
    started_at: float
    ended_at: float
    duration_ms: float
    milestones: list[MilestoneSummary] = field(default_factory=list)
    final_output: Any | None = None
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "success": self.success,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": self.duration_ms,
            "milestones": [summary.to_dict() for summary in self.milestones],
            "final_output": self.final_output,
            "errors": list(self.errors),
            "metadata": dict(self.metadata),
        }



@dataclass(frozen=True)
class RunResult:
    """Top-level execution result returned to developers."""

    success: bool
    output: Any | None = None
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    session_id: str | None = None
    session_summary: SessionSummary | None = None


@dataclass(frozen=True)
class ProposedPlan:
    """Untrusted plan proposal produced by a planner."""

    plan_description: str
    steps: list["ProposedStep"] = field(default_factory=list)
    attempt: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidatedPlan:
    """Trusted plan derived from registries and policy/trust checks."""

    plan_description: str
    steps: list["ValidatedStep"] = field(default_factory=list)
    success: bool = True
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VerifyResult:
    """Verification output for a milestone."""

    success: bool
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DonePredicate:
    """Defines what 'done' means for a Tool Loop attempt."""

    required_keys: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass(frozen=True)
class Envelope:
    """Execution boundary for the Tool Loop."""

    allowed_capability_ids: list[str] = field(default_factory=list)
    budget: Budget = field(default_factory=Budget)
    done_predicate: DonePredicate | None = None
    risk_level: RiskLevel = RiskLevel.READ_ONLY


@dataclass(frozen=True)
class ProposedStep:
    """Untrusted step proposal produced by the planner."""

    step_id: str
    capability_id: str
    params: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    envelope: Envelope | None = None


@dataclass(frozen=True)
class ValidatedStep:
    """Trusted step derived from registries and policy/trust checks.

    Trusted registry fields beyond `risk_level` are stored in `metadata`.
    """

    step_id: str
    capability_id: str
    risk_level: RiskLevel
    params: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    envelope: Envelope | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolLoopRequest:
    """Tool Loop invocation payload (capability id + params + envelope boundary)."""

    capability_id: str
    params: dict[str, Any] = field(default_factory=dict)
    envelope: Envelope = field(default_factory=Envelope)


__all__ = [
    "DonePredicate",
    "Envelope",
    "Milestone",
    "MilestoneSummary",
    "ProposedStep",
    "ProposedPlan",
    "RunResult",
    "SessionSummary",
    "Task",
    "ToolLoopRequest",
    "ValidatedStep",
    "ValidatedPlan",
    "VerifyResult",
]
