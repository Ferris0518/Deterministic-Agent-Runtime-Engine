from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time

from .config import Config
from .results import MilestoneSummary, SessionSummary
from .tool import Evidence, ToolErrorRecord


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


@dataclass
class SessionContext:
    user_input: str
    previous_session_summary: SessionSummary | None
    config: Config
    milestone_summaries: list[MilestoneSummary] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class ModelResponse:
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class GenerateOptions:
    max_tokens: int | None = None
    temperature: float | None = None


@dataclass(frozen=True)
class AssembledContext:
    messages: list[Message]
    metadata: dict[str, Any] = field(default_factory=dict)
