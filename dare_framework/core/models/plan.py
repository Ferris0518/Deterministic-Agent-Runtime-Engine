from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Optional
import time

from .runtime import new_id
from .tool import Evidence, RiskLevel, StepType


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
    task_id: str = field(default_factory=lambda: new_id("task"))
    expectations: list[Expectation] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    milestones: list["Milestone"] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_milestones(self) -> list["Milestone"]:
        if self.milestones:
            return self.milestones
        return [
            Milestone(
                milestone_id=new_id("milestone"),
                description=self.description,
                user_input=self.description,
                expectations=self.expectations,
            )
        ]


@dataclass
class Milestone:
    milestone_id: str
    description: str
    user_input: str
    order: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    expectations: list[Expectation] = field(default_factory=list)


@dataclass(frozen=True)
class PlanBudget:
    max_attempts: int = 3


@dataclass
class EnvelopeBudget:
    max_tool_calls: int = 30
    max_tokens: int = 50000
    max_wall_time_seconds: int = 180
    max_stagnant_iterations: int = 3
    current_tool_calls: int = 0
    current_attempts: int = 0
    stagnant_iterations: int = 0
    start_time: float = field(default_factory=time.time)

    def exceeded(self) -> bool:
        if self.current_tool_calls >= self.max_tool_calls:
            return True
        if time.time() - self.start_time >= self.max_wall_time_seconds:
            return True
        if self.stagnant_iterations >= self.max_stagnant_iterations:
            return True
        return False

    def record_attempt(self) -> None:
        self.current_attempts += 1

    def record_tool_call(self) -> None:
        self.current_tool_calls += 1

    def record_stagnation(self) -> None:
        self.stagnant_iterations += 1

    def record_progress(self) -> None:
        self.stagnant_iterations = 0


@dataclass
class EvidenceCondition:
    condition_type: str
    params: dict[str, Any]

    def check(self, evidence: Iterable[Evidence]) -> bool:
        if self.condition_type == "always":
            return True
        if self.condition_type == "evidence_kind":
            kind = self.params.get("kind")
            return any(item.kind == kind for item in evidence)
        return False


@dataclass(frozen=True)
class DonePredicate:
    required_keys: list[str] = field(default_factory=list)
    evidence_conditions: list[EvidenceCondition] = field(default_factory=list)
    require_all: bool = True
    description: str | None = None


@dataclass(frozen=True)
class Envelope:
    allowed_tools: list[str] = field(default_factory=list)
    required_evidence: list[EvidenceCondition] = field(default_factory=list)
    budget: EnvelopeBudget = field(default_factory=EnvelopeBudget)
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    done_predicate: DonePredicate | None = None


@dataclass(frozen=True)
class ProposedStep:
    step_id: str
    tool_name: str
    tool_input: dict[str, Any]
    description: str = ""
    envelope: Envelope | None = None
    done_predicate: DonePredicate | None = None


@dataclass(frozen=True)
class ProposedPlan:
    plan_description: str
    proposed_steps: list[ProposedStep]
    attempt: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidatedStep:
    step_id: str
    step_type: StepType
    tool_name: str
    risk_level: RiskLevel
    tool_input: dict[str, Any]
    description: str = ""
    envelope: Envelope | None = None
    done_predicate: DonePredicate | None = None


@dataclass(frozen=True)
class ValidatedPlan:
    plan_description: str
    steps: list[ValidatedStep]
    metadata: dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ValidationResult:
    success: bool
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VerifyResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
