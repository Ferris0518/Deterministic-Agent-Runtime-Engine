from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

DepsT = TypeVar("DepsT")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class RuntimeState(Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CANCELLED = "cancelled"


@dataclass
class RunContext(Generic[DepsT]):
    deps: DepsT | None
    run_id: str
    task_id: str | None = None
    milestone_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeSnapshot:
    state: RuntimeState
    task_id: str
    milestone_id: str | None
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
