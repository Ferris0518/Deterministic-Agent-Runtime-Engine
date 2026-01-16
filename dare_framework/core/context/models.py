from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generic

from dare_framework.core.component import DepsT, OutputT
from dare_framework.core.config.config import Config
from dare_framework.core.models.evidence import Evidence
from dare_framework.core.models.model_adapter import Message
from dare_framework.core.models.runtime_state import RuntimeState
from dare_framework.core.plan.models import VerifyResult
from dare_framework.core.tool.models import ToolErrorRecord, ToolResult


@dataclass(frozen=True)
class MemoryItem:
    key: str
    value: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunContext(Generic[DepsT]):
    deps: DepsT | None
    run_id: str
    task_id: str | None = None
    milestone_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    config: Config | None = None


@dataclass(frozen=True)
class AssembledContext:
    messages: list[Message]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecuteResult:
    success: bool
    outputs: list[ToolResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    encountered_plan_tool: bool = False
    plan_tool_name: str | None = None


@dataclass(frozen=True)
class MilestoneSummary:
    milestone_id: str
    description: str
    success: bool
    attempt_count: int
    evidence_count: int


@dataclass(frozen=True)
class MilestoneResult:
    success: bool
    outputs: list[ToolResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    verify_result: VerifyResult | None = None
    summary: MilestoneSummary | None = None


@dataclass(frozen=True)
class SessionSummary:
    session_id: str
    milestone_count: int
    success: bool
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SessionContext:
    user_input: str
    previous_session_summary: SessionSummary | None
    config: Config
    milestone_summaries: list[MilestoneSummary] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)


@dataclass(frozen=True)
class RuntimeSnapshot:
    state: RuntimeState
    task_id: str
    milestone_id: str | None
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MilestoneContext:
    user_input: str
    milestone_description: str
    reflections: list[str] = field(default_factory=list)
    tool_errors: list[ToolErrorRecord] = field(default_factory=list)
    evidence_collected: list[Evidence] = field(default_factory=list)
    attempted_plans: list[dict[str, Any]] = field(default_factory=list)

    def add_reflection(self, reflection: str) -> "MilestoneContext":
        self.reflections.append(reflection)
        return self

    def add_error(self, error: ToolErrorRecord) -> "MilestoneContext":
        self.tool_errors.append(error)
        return self

    def add_evidence(self, evidence: Evidence) -> "MilestoneContext":
        self.evidence_collected.append(evidence)
        return self

    def add_attempt(self, attempt: dict[str, Any]) -> "MilestoneContext":
        self.attempted_plans.append(attempt)
        return self


@dataclass(frozen=True)
class RunResult(Generic[OutputT]):
    success: bool
    output: OutputT | None = None
    milestone_results: list[MilestoneResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    session_summary: SessionSummary | None = None

