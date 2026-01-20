"""Agent runtime wrapper for v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dare_framework3._internal.execution.kernel import IRunLoop
from dare_framework3._internal.plan.types import Task, RunResult


@dataclass
class Agent:
    """Developer-facing agent wrapper around a run loop."""

    name: str
    run_loop: IRunLoop

    async def run(self, task: Task | str, *, deps: Any | None = None) -> RunResult:
        _ = deps
        task_obj = task if isinstance(task, Task) else Task(description=task)
        return await self.run_loop.run(task_obj)
