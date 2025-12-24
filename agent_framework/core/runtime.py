from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from uuid import uuid4

from ..components.checkpoint import FileCheckpoint
from ..components.context_assembler import BasicContextAssembler
from ..components.event_log import LocalEventLog
from ..components.policy_engine import AllowAllPolicyEngine
from ..components.remediator import NoOpRemediator
from ..components.validator import SimpleValidator
from .interfaces import (
    ICheckpoint,
    IContextAssembler,
    IEventLog,
    IPlanGenerator,
    IPolicyEngine,
    IRemediator,
    IRuntime,
    IToolRuntime,
    IValidator,
)
from .models import (
    Event,
    ExecuteResult,
    Milestone,
    MilestoneResult,
    PlanBudget,
    RunContext,
    RunResult,
    RuntimeSnapshot,
    RuntimeState,
    Task,
    VerifyResult,
    ValidatedPlan,
)

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


@dataclass
class PlanLoopOutcome:
    validated_plan: ValidatedPlan | None
    reflection: str | None
    errors: list[str]


class AgentRuntime(IRuntime[DepsT, OutputT], Generic[DepsT, OutputT]):
    def __init__(
        self,
        tool_runtime: IToolRuntime,
        plan_generator: IPlanGenerator,
        validator: IValidator | None = None,
        policy_engine: IPolicyEngine | None = None,
        remediator: IRemediator | None = None,
        context_assembler: IContextAssembler | None = None,
        event_log: IEventLog | None = None,
        checkpoint: ICheckpoint | None = None,
    ) -> None:
        self._tool_runtime = tool_runtime
        self._plan_generator = plan_generator
        self._validator = validator or SimpleValidator()
        self._policy_engine = policy_engine or AllowAllPolicyEngine()
        self._remediator = remediator or NoOpRemediator()
        self._context_assembler = context_assembler or BasicContextAssembler()
        self._event_log = event_log or LocalEventLog()
        self._checkpoint = checkpoint or FileCheckpoint()
        self._state = RuntimeState.READY
        self._active_task: Task | None = None
        self._run_id: str | None = None

    async def init(self, task: Task) -> None:
        self._active_task = task
        self._state = RuntimeState.READY
        await self._log_event("runtime.init", {"task_id": task.task_id})

    async def run(self, task: Task, deps: DepsT) -> RunResult[OutputT]:
        if self._state not in {RuntimeState.READY, RuntimeState.PAUSED}:
            raise RuntimeError(f"Runtime state invalid for run: {self._state}")
        if self._active_task is None or self._active_task.task_id != task.task_id:
            self._active_task = task
        self._state = RuntimeState.RUNNING
        self._run_id = uuid4().hex
        await self._log_event("runtime.run", {"task_id": task.task_id, "run_id": self._run_id})

        milestone_results: list[MilestoneResult] = []
        errors: list[str] = []
        for milestone in task.to_milestones():
            ctx = RunContext(
                run_id=self._run_id,
                task_id=task.task_id,
                milestone_id=milestone.milestone_id,
                reflections=[],
            )
            result = await self._milestone_loop(milestone, ctx)
            milestone_results.append(result)
            if not result.success:
                errors.extend(result.errors)
                break

        success = not errors
        output = milestone_results[-1].outputs if milestone_results else None
        await self._log_event(
            "runtime.complete",
            {"task_id": task.task_id, "run_id": self._run_id, "success": success},
        )
        self._state = RuntimeState.STOPPED if success else RuntimeState.CANCELLED
        return RunResult(success=success, output=output, milestone_results=milestone_results, errors=errors)

    async def pause(self) -> None:
        if self._state != RuntimeState.RUNNING:
            return
        snapshot = RuntimeSnapshot(
            state=self._state,
            task_id=self._active_task.task_id if self._active_task else "",
            milestone_id=None,
        )
        checkpoint_id = await self._checkpoint.save(snapshot)
        await self._log_event("runtime.pause", {"checkpoint_id": checkpoint_id})
        self._state = RuntimeState.PAUSED

    async def resume(self) -> None:
        if self._state != RuntimeState.PAUSED:
            return
        self._state = RuntimeState.RUNNING
        await self._log_event("runtime.resume", {"task_id": self._active_task.task_id if self._active_task else ""})

    async def stop(self) -> None:
        self._state = RuntimeState.STOPPED
        await self._log_event("runtime.stop", {"task_id": self._active_task.task_id if self._active_task else ""})

    async def cancel(self) -> None:
        self._state = RuntimeState.CANCELLED
        await self._log_event("runtime.cancel", {"task_id": self._active_task.task_id if self._active_task else ""})

    def get_state(self) -> RuntimeState:
        return self._state

    async def _milestone_loop(self, milestone: Milestone, ctx: RunContext) -> MilestoneResult:
        await self._log_event(
            "milestone.start",
            {"milestone_id": milestone.milestone_id, "run_id": ctx.run_id},
        )
        plan_budget = PlanBudget()
        for attempt in range(plan_budget.max_attempts):
            plan_outcome = await self._plan_loop(milestone, ctx, attempt)
            if not plan_outcome.validated_plan:
                ctx.reflections.append(plan_outcome.reflection or "plan failed")
                continue

            if self._policy_engine.needs_approval(milestone, plan_outcome.validated_plan):
                await self.pause()
                await self.resume()

            execute_result = await self._execute_loop(plan_outcome.validated_plan, ctx)
            if execute_result.encountered_plan_tool:
                ctx.reflections.append(f"plan tool encountered: {execute_result.plan_tool_name}")
                continue

            verify_result = await self._validator.validate_milestone(milestone, execute_result, ctx)
            if verify_result.success:
                await self._log_event(
                    "milestone.success",
                    {
                        "milestone_id": milestone.milestone_id,
                        "run_id": ctx.run_id,
                    },
                )
                return MilestoneResult(
                    success=True,
                    outputs=execute_result.outputs,
                    errors=[],
                    verify_result=verify_result,
                )

            reflection = await self._remediator.remediate(verify_result, verify_result.errors, ctx)
            ctx.reflections.append(reflection)

        await self._log_event(
            "milestone.failed",
            {"milestone_id": milestone.milestone_id, "run_id": ctx.run_id},
        )
        return MilestoneResult(success=False, outputs=[], errors=["milestone failed"], verify_result=None)

    async def _plan_loop(self, milestone: Milestone, ctx: RunContext, attempt: int) -> PlanLoopOutcome:
        context_messages = await self._context_assembler.assemble(milestone, ctx)
        ctx.metadata["context_messages"] = context_messages
        proposed_plan = await self._plan_generator.generate_plan(milestone, ctx, attempt)
        await self._log_event(
            "plan.attempt",
            {"milestone_id": milestone.milestone_id, "attempt": attempt, "run_id": ctx.run_id},
        )
        validation = await self._validator.validate_plan(proposed_plan.steps, ctx)
        if validation.success:
            await self._log_event(
                "plan.validated",
                {"milestone_id": milestone.milestone_id, "run_id": ctx.run_id},
            )
            validated = ValidatedPlan(steps=proposed_plan.steps, summary=proposed_plan.summary)
            return PlanLoopOutcome(validated_plan=validated, reflection=None, errors=[])

        await self._log_event(
            "plan.invalid",
            {
                "milestone_id": milestone.milestone_id,
                "run_id": ctx.run_id,
                "errors": validation.errors,
            },
        )
        reflection = await self._remediator.remediate(
            VerifyResult(success=False, errors=validation.errors, evidence={}),
            validation.errors,
            ctx,
        )
        return PlanLoopOutcome(validated_plan=None, reflection=reflection, errors=validation.errors)

    async def _execute_loop(self, plan: ValidatedPlan, ctx: RunContext) -> ExecuteResult:
        outputs: list = []
        errors: list[str] = []
        for step in plan.steps:
            if self._tool_runtime.is_plan_tool(step.tool_name):
                await self._log_event(
                    "plan.tool_encountered",
                    {"tool": step.tool_name, "run_id": ctx.run_id, "step_id": step.step_id},
                )
                return ExecuteResult(
                    success=False,
                    outputs=outputs,
                    errors=errors,
                    encountered_plan_tool=True,
                    plan_tool_name=step.tool_name,
                )
            try:
                await self._log_event(
                    "tool.invoke",
                    {"tool": step.tool_name, "run_id": ctx.run_id, "step_id": step.step_id},
                )
                result = await self._tool_runtime.invoke(
                    step.tool_name,
                    step.tool_input,
                    ctx,
                    envelope=step.envelope,
                )
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))
                await self._log_event(
                    "tool.error",
                    {"tool": step.tool_name, "error": str(exc), "run_id": ctx.run_id},
                )
                return ExecuteResult(success=False, outputs=outputs, errors=errors)
            outputs.append(result)
            if not result.success:
                errors.append(result.error or "tool failed")
        return ExecuteResult(success=not errors, outputs=outputs, errors=errors)

    async def _log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        await self._event_log.append(Event(event_type=event_type, payload=payload))
