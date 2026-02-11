"""Plan tools: read/write PlannerState. Used by Plan Agent when Planner is mounted as IToolProvider."""

from __future__ import annotations

from typing import Any

from dare_framework.tool.kernel import ITool
from dare_framework.tool.types import (
    CapabilityKind,
    RiskLevelName,
    RunContext,
    ToolResult,
    ToolType,
)
from dare_framework.tool._internal.util.__tool_schema_util import (
    infer_input_schema_from_execute,
    infer_output_schema_from_execute,
)

from dare_framework.plan_v2.types import Milestone, PlannerState, Step


class CreatePlanTool(ITool):
    """Create or replace the current plan (description + steps) for the current milestone/task."""

    def __init__(self, state: PlannerState) -> None:
        self._state = state

    @property
    def name(self) -> str:
        return "create_plan"

    @property
    def description(self) -> str:
        return (
            "Create or replace the current plan. Provide plan_description and a list of steps. "
            "Each step has step_id, description, and optional params (executor chooses tools)."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return infer_input_schema_from_execute(type(self).execute)

    @property
    def output_schema(self) -> dict[str, Any] | None:
        return infer_output_schema_from_execute(type(self).execute)

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ATOMIC

    @property
    def risk_level(self) -> RiskLevelName:
        return "read_only"

    @property
    def requires_approval(self) -> bool:
        return False

    @property
    def timeout_seconds(self) -> int:
        return 30

    @property
    def is_work_unit(self) -> bool:
        return False

    @property
    def capability_kind(self) -> CapabilityKind:
        return CapabilityKind.PLAN_TOOL

    async def execute(
        self,
        *,
        run_context: RunContext[Any],
        plan_description: str,
        steps: list[dict[str, Any]],
        **kwargs: Any,
    ) -> ToolResult[dict[str, Any]]:
        """Write plan to PlannerState.

        Args:
            run_context: Runtime context.
            plan_description: Short description of the plan.
            steps: List of {"step_id": str, "description": str, "params": dict}.
        """
        self._state.plan_description = plan_description
        self._state.steps = [
            Step(
                step_id=s.get("step_id", ""),
                description=s.get("description", ""),
                params=s.get("params") or {},
            )
            for s in steps
        ]
        return ToolResult(success=True, output={"plan_description": plan_description, "steps_count": len(self._state.steps)})


class ValidatePlanTool(ITool):
    """Mark the current plan as validated or record validation errors (e.g. from external validator)."""

    def __init__(self, state: PlannerState) -> None:
        self._state = state

    @property
    def name(self) -> str:
        return "validate_plan"

    @property
    def description(self) -> str:
        return "Set plan validation result: success and optional list of error messages."

    @property
    def input_schema(self) -> dict[str, Any]:
        return infer_input_schema_from_execute(type(self).execute)

    @property
    def output_schema(self) -> dict[str, Any] | None:
        return infer_output_schema_from_execute(type(self).execute)

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ATOMIC

    @property
    def risk_level(self) -> RiskLevelName:
        return "read_only"

    @property
    def requires_approval(self) -> bool:
        return False

    @property
    def timeout_seconds(self) -> int:
        return 15

    @property
    def is_work_unit(self) -> bool:
        return False

    @property
    def capability_kind(self) -> CapabilityKind:
        return CapabilityKind.PLAN_TOOL

    async def execute(
        self,
        *,
        run_context: RunContext[Any],
        success: bool = True,
        errors: list[str] | None = None,
        **kwargs: Any,
    ) -> ToolResult[dict[str, Any]]:
        """Write validation result to PlannerState."""
        self._state.plan_success = success
        self._state.plan_errors = list(errors or [])
        return ToolResult(success=True, output={"plan_success": success, "errors": self._state.plan_errors})


class VerifyMilestoneTool(ITool):
    """Record milestone verification result (errors if not met)."""

    def __init__(self, state: PlannerState) -> None:
        self._state = state

    @property
    def name(self) -> str:
        return "verify_milestone"

    @property
    def description(self) -> str:
        return "Set milestone verification result: list of error messages if not met, empty if success."

    @property
    def input_schema(self) -> dict[str, Any]:
        return infer_input_schema_from_execute(type(self).execute)

    @property
    def output_schema(self) -> dict[str, Any] | None:
        return infer_output_schema_from_execute(type(self).execute)

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ATOMIC

    @property
    def risk_level(self) -> RiskLevelName:
        return "read_only"

    @property
    def requires_approval(self) -> bool:
        return False

    @property
    def timeout_seconds(self) -> int:
        return 15

    @property
    def is_work_unit(self) -> bool:
        return False

    @property
    def capability_kind(self) -> CapabilityKind:
        return CapabilityKind.PLAN_TOOL

    async def execute(
        self,
        *,
        run_context: RunContext[Any],
        errors: list[str] | None = None,
        **kwargs: Any,
    ) -> ToolResult[dict[str, Any]]:
        """Write verify result to PlannerState."""
        self._state.last_verify_errors = list(errors or [])
        return ToolResult(success=True, output={"verify_errors": self._state.last_verify_errors})


class ReflectTool(ITool):
    """Record remediation/reflection summary for the current milestone."""

    def __init__(self, state: PlannerState) -> None:
        self._state = state

    @property
    def name(self) -> str:
        return "reflect"

    @property
    def description(self) -> str:
        return "Record a short remediation or reflection summary (e.g. after verification failure)."

    @property
    def input_schema(self) -> dict[str, Any]:
        return infer_input_schema_from_execute(type(self).execute)

    @property
    def output_schema(self) -> dict[str, Any] | None:
        return infer_output_schema_from_execute(type(self).execute)

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ATOMIC

    @property
    def risk_level(self) -> RiskLevelName:
        return "read_only"

    @property
    def requires_approval(self) -> bool:
        return False

    @property
    def timeout_seconds(self) -> int:
        return 15

    @property
    def is_work_unit(self) -> bool:
        return False

    @property
    def capability_kind(self) -> CapabilityKind:
        return CapabilityKind.PLAN_TOOL

    async def execute(
        self,
        *,
        run_context: RunContext[Any],
        summary: str,
        **kwargs: Any,
    ) -> ToolResult[dict[str, Any]]:
        """Write remediation summary to PlannerState."""
        self._state.last_remediation_summary = summary
        return ToolResult(success=True, output={"remediation_summary": summary})


class DecomposeTaskTool(ITool):
    """Decompose task into milestones and optionally set current milestone."""

    def __init__(self, state: PlannerState) -> None:
        self._state = state

    @property
    def name(self) -> str:
        return "decompose_task"

    @property
    def description(self) -> str:
        return (
            "Set the list of milestones for the current task. Each milestone has "
            "milestone_id, description, success_criteria (list), optional metadata."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return infer_input_schema_from_execute(type(self).execute)

    @property
    def output_schema(self) -> dict[str, Any] | None:
        return infer_output_schema_from_execute(type(self).execute)

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ATOMIC

    @property
    def risk_level(self) -> RiskLevelName:
        return "read_only"

    @property
    def requires_approval(self) -> bool:
        return False

    @property
    def timeout_seconds(self) -> int:
        return 30

    @property
    def is_work_unit(self) -> bool:
        return False

    @property
    def capability_kind(self) -> CapabilityKind:
        return CapabilityKind.PLAN_TOOL

    async def execute(
        self,
        *,
        run_context: RunContext[Any],
        milestones: list[dict[str, Any]],
        current_milestone_id: str | None = None,
        **kwargs: Any,
    ) -> ToolResult[dict[str, Any]]:
        """Write milestones to PlannerState and optionally set current_milestone_id."""
        self._state.milestones = [
            Milestone(
                milestone_id=m.get("milestone_id", ""),
                description=m.get("description", ""),
                success_criteria=m.get("success_criteria") or [],
                metadata=m.get("metadata") or {},
            )
            for m in milestones
        ]
        if current_milestone_id is not None:
            self._state.current_milestone_id = current_milestone_id
        elif self._state.milestones and not self._state.current_milestone_id:
            self._state.current_milestone_id = self._state.milestones[0].milestone_id
        return ToolResult(
            success=True,
            output={"milestones_count": len(self._state.milestones), "current_milestone_id": self._state.current_milestone_id},
        )


class DelegateToSubAgentTool(ITool):
    """Placeholder: delegate a sub-task to another agent (orchestrator uses this)."""

    def __init__(self, state: PlannerState) -> None:
        self._state = state

    @property
    def name(self) -> str:
        return "delegate_to_sub_agent"

    @property
    def description(self) -> str:
        return "Request delegation of a sub-task to another agent. Used by meta-planner; implementation is orchestrator-specific."

    @property
    def input_schema(self) -> dict[str, Any]:
        return infer_input_schema_from_execute(type(self).execute)

    @property
    def output_schema(self) -> dict[str, Any] | None:
        return infer_output_schema_from_execute(type(self).execute)

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ATOMIC

    @property
    def risk_level(self) -> RiskLevelName:
        return "read_only"

    @property
    def requires_approval(self) -> bool:
        return False

    @property
    def timeout_seconds(self) -> int:
        return 5

    @property
    def is_work_unit(self) -> bool:
        return False

    @property
    def capability_kind(self) -> CapabilityKind:
        return CapabilityKind.PLAN_TOOL

    async def execute(
        self,
        *,
        run_context: RunContext[Any],
        sub_task_description: str,
        **kwargs: Any,
    ) -> ToolResult[dict[str, Any]]:
        """Stub: actual delegation is done by orchestrator."""
        return ToolResult(
            success=True,
            output={"delegated": sub_task_description, "note": "Orchestrator should handle delegation."},
        )


__all__ = [
    "CreatePlanTool",
    "DecomposeTaskTool",
    "DelegateToSubAgentTool",
    "ReflectTool",
    "ValidatePlanTool",
    "VerifyMilestoneTool",
]
