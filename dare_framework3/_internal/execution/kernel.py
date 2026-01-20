"""Execution domain kernel interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Protocol, Sequence

from dare_framework3._internal.execution.types import (
    RunLoopState,
    TickResult,
    ExecutionSignal,
    Budget,
    ResourceType,
    Event,
    RuntimeSnapshot,
    HookPhase,
)

if TYPE_CHECKING:
    from dare_framework3._internal.plan.types import (
        Task,
        Milestone,
        ValidatedPlan,
        ToolLoopRequest,
        RunResult,
        MilestoneResult,
        ExecuteResult,
        ToolLoopResult,
    )


class IRunLoop(Protocol):
    """Tick-based run surface for the Kernel."""

    @property
    def state(self) -> RunLoopState:
        """Current run loop state."""
        ...

    async def tick(self) -> TickResult:
        """Execute a minimal scheduling step."""
        ...

    async def run(self, task: "Task") -> "RunResult":
        """Drive execution until termination."""
        ...


class ILoopOrchestrator(Protocol):
    """Five-layer loop skeleton."""

    async def run_session_loop(self, task: "Task") -> "RunResult":
        ...

    async def run_milestone_loop(self, milestone: "Milestone") -> "MilestoneResult":
        ...

    async def run_plan_loop(self, milestone: "Milestone") -> "ValidatedPlan":
        ...

    async def run_execute_loop(self, plan: "ValidatedPlan") -> "ExecuteResult":
        ...

    async def run_tool_loop(self, req: "ToolLoopRequest") -> "ToolLoopResult":
        ...


class IExecutionControl(Protocol):
    """Pause/resume/checkpoint control plane."""

    def poll(self) -> ExecutionSignal:
        ...

    def poll_or_raise(self) -> None:
        ...

    async def pause(self, reason: str) -> str:
        ...

    async def resume(self, checkpoint_id: str) -> None:
        ...

    async def checkpoint(self, label: str, payload: dict[str, Any]) -> str:
        ...

    async def wait_for_human(self, checkpoint_id: str, reason: str) -> None:
        ...


class IResourceManager(Protocol):
    """Unified budget model and accounting."""

    def get_budget(self) -> Budget:
        ...

    def debit(self, resource_type: ResourceType, amount: float) -> None:
        ...

    def credit(self, resource_type: ResourceType, amount: float) -> None:
        ...

    def snapshot(self) -> dict[str, float]:
        ...


class IEventLog(Protocol):
    """Immutable event log for audit and tracing."""

    async def append(self, event: Event) -> None:
        ...

    async def list(self, *, since: float | None = None) -> Sequence[Event]:
        ...

    async def snapshot(self) -> RuntimeSnapshot:
        ...


class IExtensionPoint(Protocol):
    """Kernel extension point for hooks."""

    def register(self, phase: HookPhase, hook: Callable[[dict[str, Any]], Any]) -> None:
        ...

    async def emit(self, phase: HookPhase, payload: dict[str, Any]) -> None:
        ...
