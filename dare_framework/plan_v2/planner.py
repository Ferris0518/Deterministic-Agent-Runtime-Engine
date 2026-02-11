"""Planner: holds PlannerState and exposes plan tools as IToolProvider. Mount on ReactAgent as Plan Agent."""

from __future__ import annotations

from dare_framework.tool.kernel import ITool, IToolProvider

from dare_framework.plan_v2.types import PlannerState
from dare_framework.plan_v2.tools import (
    CreatePlanTool,
    DecomposeTaskTool,
    DelegateToSubAgentTool,
    ReflectTool,
    ValidatePlanTool,
    VerifyMilestoneTool,
)


class Planner(IToolProvider):
    """Plan state + plan tools. Register as a tool provider to get a Plan Agent (ReactAgent + this)."""

    def __init__(self, state: PlannerState | None = None) -> None:
        self._state = state if state is not None else PlannerState()
        self._tools: list[ITool] = [
            CreatePlanTool(self._state),
            ValidatePlanTool(self._state),
            VerifyMilestoneTool(self._state),
            ReflectTool(self._state),
            DecomposeTaskTool(self._state),
            DelegateToSubAgentTool(self._state),
        ]

    @property
    def state(self) -> PlannerState:
        """PlannerState for this planner. Orchestrator can read it and call copy_for_execution() for Execution Agent."""
        return self._state

    def list_tools(self) -> list[ITool]:
        return list(self._tools)


__all__ = ["Planner"]
