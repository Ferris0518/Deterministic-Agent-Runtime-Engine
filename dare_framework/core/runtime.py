from __future__ import annotations

from typing import Generic, Protocol, TypeVar, runtime_checkable

from .models.event import Event, EventFilter
from .models.plan import Task
from .models.results import RunResult
from .models.runtime import RuntimeSnapshot, RuntimeState
from .composition import IConfigurableComponent

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


class IEventLog(Protocol):
    """Append-only event log for audit and WORM guarantees (Architecture_Final_Review_v1.3)."""

    async def append(self, event: Event) -> str:
        """Append an event and return its event identifier or hash."""
        ...

    async def query(self, filter: EventFilter | None = None, offset: int = 0, limit: int = 100) -> list[Event]:
        """Query a window of events for replay or inspection."""
        ...

    async def verify_chain(self) -> bool:
        """Verify hash-chain integrity for audit purposes."""
        ...

    async def get_checkpoint_events(self, checkpoint_id: str) -> list[Event]:
        """Return events associated with a checkpoint."""
        ...


class ICheckpoint(Protocol):
    """Snapshot storage for runtime state across context windows (Architecture_Final_Review_v1.3)."""

    async def save(self, snapshot: RuntimeSnapshot) -> str:
        """Persist a runtime snapshot and return checkpoint id."""
        ...

    async def load(self, checkpoint_id: str) -> RuntimeSnapshot:
        """Load a previously saved runtime snapshot."""
        ...


@runtime_checkable
class IHook(IConfigurableComponent, Protocol):
    """Lifecycle hooks for observing runtime events (Interface_Layer_Design_v1.1)."""

    async def on_event(self, event: Event) -> None:
        """Handle a runtime event for logging or metrics."""
        ...
