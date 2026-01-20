"""Execution domain data types."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RunLoopState(Enum):
    """Lifecycle state for the run loop."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionSignal(Enum):
    """Control-plane signals for execution."""

    NONE = "none"
    PAUSE = "pause"
    CANCEL = "cancel"
    APPROVAL_REQUIRED = "approval_required"


class ResourceType(Enum):
    """Resource types tracked by the budget manager."""

    TOKENS = "tokens"
    COST = "cost"
    TIME_SECONDS = "time_seconds"
    TOOL_CALLS = "tool_calls"


class HookPhase(Enum):
    """Kernel hook phases."""

    BEFORE_RUN = "before_run"
    AFTER_RUN = "after_run"
    BEFORE_TICK = "before_tick"
    AFTER_TICK = "after_tick"
    BEFORE_TOOL = "before_tool"
    AFTER_TOOL = "after_tool"


@dataclass(frozen=True)
class Budget:
    """Unified execution budget."""

    max_tokens: int | None = None
    max_cost: float | None = None
    max_time_seconds: int | None = None
    max_tool_calls: int | None = None


@dataclass(frozen=True)
class Event:
    """Canonical event record."""

    event_id: str
    kind: str
    payload: dict[str, Any]
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class RuntimeSnapshot:
    """Minimal runtime snapshot for audit/debugging."""

    run_id: str
    state: RunLoopState
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TickResult:
    """Result of a single scheduler tick."""

    state: RunLoopState
    events: list[Event] = field(default_factory=list)
    snapshot: RuntimeSnapshot | None = None
