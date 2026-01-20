"""Plan domain data types.

VAF simplified version - only essential types retained.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from vaf.utils.ids import generate_id


# =============================================================================
# Step - A single step in a plan (replaces Milestone)
# =============================================================================

@dataclass
class Step:
    """A single step in a plan.
    
    Simplified replacement for the old Milestone type.
    
    Attributes:
        step_id: Unique step identifier
        name: Short name for the step
        description: Detailed description of what this step does
        state: Current execution state
        outcome: The actual outcome after execution
        created_at: When the step was created
        finished_at: When the step was completed
    """
    step_id: str
    name: str
    description: str
    state: Literal["pending", "in_progress", "done", "failed"] = "pending"
    outcome: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    
    def start(self) -> None:
        """Mark the step as in progress."""
        self.state = "in_progress"
    
    def finish(self, outcome: str, success: bool = True) -> None:
        """Mark the step as completed."""
        self.state = "done" if success else "failed"
        self.outcome = outcome
        self.finished_at = datetime.now(timezone.utc)


# =============================================================================
# Plan - A collection of steps
# =============================================================================

@dataclass
class Plan:
    """An execution plan containing multiple steps.
    
    Attributes:
        plan_id: Unique plan identifier
        name: Short name for the plan
        description: What this plan aims to achieve
        steps: List of steps to execute
        state: Current execution state
        created_at: When the plan was created
    """
    plan_id: str
    name: str
    description: str
    steps: list[Step] = field(default_factory=list)
    state: Literal["pending", "in_progress", "done", "failed"] = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_step(self, name: str, description: str) -> Step:
        """Add a new step to the plan."""
        step = Step(
            step_id=generate_id("step"),
            name=name,
            description=description,
        )
        self.steps.append(step)
        return step
    
    def get_next_pending_step(self) -> Step | None:
        """Get the next pending step."""
        for step in self.steps:
            if step.state == "pending":
                return step
        return None
    
    def is_complete(self) -> bool:
        """Check if all steps are done."""
        return all(step.state in ("done", "failed") for step in self.steps)
    
    def refresh_state(self) -> None:
        """Update plan state based on step states."""
        if all(step.state == "done" for step in self.steps):
            self.state = "done"
        elif any(step.state == "failed" for step in self.steps):
            self.state = "failed"
        elif any(step.state == "in_progress" for step in self.steps):
            self.state = "in_progress"


# =============================================================================
# Task - High-level user request
# =============================================================================

@dataclass
class Task:
    """A high-level execution request from the user.
    
    Attributes:
        description: The task description
        task_id: Unique identifier (auto-generated if not provided)
        context: Additional context data
        created_at: Task creation timestamp
    """
    description: str
    task_id: str = field(default_factory=lambda: generate_id("task"))
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_step(self) -> Step:
        """Convert task to a single step (for simple execution)."""
        return Step(
            step_id=generate_id("step"),
            name="Execute task",
            description=self.description,
        )


# =============================================================================
# RunResult - Agent execution result
# =============================================================================

@dataclass
class RunResult:
    """Top-level execution result returned to developers.
    
    Attributes:
        success: Whether the run succeeded
        output: Final output content
        errors: Error messages if any
        metadata: Additional result metadata
    """
    success: bool
    output: Any | None = None
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
