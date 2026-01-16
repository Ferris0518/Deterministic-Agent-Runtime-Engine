from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from dare_framework.core.plan.models import Task
from dare_framework.core.context.models import RunResult
from .models.runtime_state import RuntimeState

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


class IRuntime(Protocol, Generic[DepsT, OutputT]):
    """Executes the five-loop runtime (Architecture_Final_Review_v1.3)."""

    async def init(self, task: Task) -> None:
        """Prepare runtime state for the incoming task."""
        ...

    async def run(self, task: Task, deps: DepsT) -> RunResult[OutputT]:
        """Run the task to completion or interruption, emitting a RunResult."""
        ...

    async def pause(self) -> None:
        """Pause execution without discarding runtime state."""
        ...

    async def resume(self) -> None:
        """Resume execution from a paused state."""
        ...

    async def stop(self) -> None:
        """Stop execution gracefully and finalize state."""
        ...

    async def cancel(self) -> None:
        """Cancel execution and mark the run as aborted."""
        ...

    def get_state(self) -> RuntimeState:
        """Return the current runtime lifecycle state."""
        ...
