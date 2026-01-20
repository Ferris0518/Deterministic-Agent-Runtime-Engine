"""No-op run loop placeholder."""

from __future__ import annotations

from dare_framework3._internal.execution.kernel import IRunLoop
from dare_framework3._internal.execution.types import RunLoopState, TickResult
from dare_framework3._internal.plan.types import Task, RunResult


class NoOpRunLoop(IRunLoop):
    """Minimal run loop that returns a failed result."""

    def __init__(self) -> None:
        self._state = RunLoopState.IDLE

    @property
    def state(self) -> RunLoopState:
        return self._state

    async def tick(self) -> TickResult:
        self._state = RunLoopState.COMPLETED
        return TickResult(state=self._state, events=[])

    async def run(self, task: Task) -> RunResult:
        _ = task
        self._state = RunLoopState.RUNNING
        self._state = RunLoopState.COMPLETED
        return RunResult(success=False, output=None, errors=["No run loop configured"])
