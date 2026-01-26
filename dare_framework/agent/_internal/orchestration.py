"""Orchestration state management for the five-layer loop.

This module provides state holders used during five-layer loop execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from dare_framework.plan.types import Milestone


@dataclass
class MilestoneState:
    """Internal milestone state holder used for plan isolation and verification."""

    milestone: Milestone
    reflections: list[str] = field(default_factory=list)
    attempted_plans: list[dict[str, Any]] = field(default_factory=list)
    evidence_collected: list[Any] = field(default_factory=list)

    def add_reflection(self, text: str) -> None:
        """Add a reflection note (e.g., from remediation)."""
        self.reflections.append(text)

    def add_attempt(self, attempt: dict[str, Any]) -> None:
        """Record a plan attempt (for debugging/audit)."""
        self.attempted_plans.append(attempt)

    def add_evidence(self, evidence: Any) -> None:
        """Collect evidence from tool execution."""
        self.evidence_collected.append(evidence)


@dataclass
class SessionState:
    """Session-level state holder."""

    task_id: str
    run_id: str = field(default_factory=lambda: uuid4().hex)
    milestone_states: list[MilestoneState] = field(default_factory=list)
    current_milestone_idx: int = 0

    @property
    def current_milestone_state(self) -> MilestoneState | None:
        """Get the current milestone state, if any."""
        if 0 <= self.current_milestone_idx < len(self.milestone_states):
            return self.milestone_states[self.current_milestone_idx]
        return None


__all__ = ["MilestoneState", "SessionState"]
