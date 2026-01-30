"""Simple deterministic planner for testing and baseline scenarios.

This planner provides deterministic, rule-based plan generation for testing
and scenarios where LLM-based planning is not required.
"""

from __future__ import annotations

from typing import Any, Literal

from dare_framework.context.kernel import IContext
from dare_framework.infra.component import ComponentType
from dare_framework.plan.interfaces import IPlanner
from dare_framework.plan.types import Milestone, ProposedPlan, ProposedStep, Task


class SimplePlanner(IPlanner):
    """Deterministic planner that creates simple single-step plans.

    Useful for testing, demos, and scenarios requiring predictable behavior.
    """

    def __init__(
        self,
        default_capability_id: str = "noop",
        name: str = "simple_planner",
    ) -> None:
        self._default_capability_id = default_capability_id
        self._name = name

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.PLANNER]:
        """Component category for config scoping."""
        return ComponentType.PLANNER

    async def plan(self, ctx: IContext) -> ProposedPlan:
        """Generate a simple single-step plan.

        The plan consists of a single step using the default capability.
        The step description is derived from the context's task description
        (stored in metadata).
        """
        # Extract task info from context metadata
        metadata = ctx.config or {}
        task_desc = metadata.get("task_description", "Execute task")
        milestone_desc = metadata.get("milestone_description", task_desc)
        milestone_id = metadata.get("milestone_id", "milestone_001")

        # Generate step_id deterministically
        step_id = f"{milestone_id}_step_1"

        step = ProposedStep(
            step_id=step_id,
            capability_id=self._default_capability_id,
            params={"description": milestone_desc},
            description=milestone_desc,
        )

        return ProposedPlan(
            plan_description=f"Execute: {milestone_desc}",
            steps=[step],
            attempt=metadata.get("plan_attempt", 0),
            metadata={
                "planner": "simple",
                "milestone_id": milestone_id,
            },
        )


class SequentialPlanner(IPlanner):
    """Deterministic planner that creates sequential multi-step plans.

    Useful for workflows with predefined step sequences.
    """

    def __init__(
        self,
        steps_config: list[dict[str, Any]] | None = None,
        name: str = "sequential_planner",
    ) -> None:
        """Initialize with step configurations.

        Args:
            steps_config: List of step configs, each with:
                - capability_id: str
                - params: dict (optional)
                - description: str (optional)
            name: Component name
        """
        self._steps_config = steps_config or []
        self._name = name

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.PLANNER]:
        """Component category for config scoping."""
        return ComponentType.PLANNER

    async def plan(self, ctx: IContext) -> ProposedPlan:
        """Generate a sequential multi-step plan."""
        metadata = ctx.config or {}
        task_desc = metadata.get("task_description", "Execute task")
        milestone_id = metadata.get("milestone_id", "milestone_001")
        attempt = metadata.get("plan_attempt", 0)

        steps: list[ProposedStep] = []
        for i, step_config in enumerate(self._steps_config):
            step = ProposedStep(
                step_id=f"{milestone_id}_step_{i + 1}",
                capability_id=step_config.get("capability_id", "noop"),
                params=step_config.get("params", {}),
                description=step_config.get("description", f"Step {i + 1}"),
            )
            steps.append(step)

        # If no steps configured, create a noop step
        if not steps:
            steps.append(
                ProposedStep(
                    step_id=f"{milestone_id}_step_1",
                    capability_id="noop",
                    params={},
                    description="No-op step",
                )
            )

        return ProposedPlan(
            plan_description=f"Sequential plan: {task_desc}",
            steps=steps,
            attempt=attempt,
            metadata={
                "planner": "sequential",
                "milestone_id": milestone_id,
                "step_count": len(steps),
            },
        )


__all__ = ["SequentialPlanner", "SimplePlanner"]
