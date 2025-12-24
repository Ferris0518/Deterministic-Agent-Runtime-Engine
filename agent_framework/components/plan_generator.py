from __future__ import annotations

from typing import Iterable

from ..core.interfaces import IPlanGenerator
from ..core.models import Milestone, PlanStep, ProposedPlan, RunContext


class DeterministicPlanGenerator(IPlanGenerator):
    def __init__(self, plans: Iterable[list[PlanStep]]):
        self._plans = list(plans)

    async def generate_plan(self, milestone: Milestone, ctx: RunContext, attempt: int) -> ProposedPlan:
        index = min(attempt, len(self._plans) - 1)
        steps = self._plans[index] if self._plans else []
        return ProposedPlan(steps=steps, summary=milestone.description, attempt=attempt)
