from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar

from .plan import VerifyResult
from .tool import ToolResult

OutputT = TypeVar("OutputT")


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
class SessionSummary:
    session_id: str
    milestone_count: int
    success: bool
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class MilestoneResult:
    success: bool
    outputs: list[ToolResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    verify_result: VerifyResult | None = None
    summary: MilestoneSummary | None = None


@dataclass(frozen=True)
class RunResult(Generic[OutputT]):
    success: bool
    output: OutputT | None = None
    milestone_results: list[MilestoneResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    session_summary: SessionSummary | None = None
