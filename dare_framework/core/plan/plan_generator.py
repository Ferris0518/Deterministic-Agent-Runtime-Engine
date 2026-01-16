from __future__ import annotations

from typing import Any, Protocol

from dare_framework.core.context.models import MilestoneContext, RunContext
from dare_framework.core.plan.models import Milestone, ProposedPlan


class IPlanGenerator(Protocol):
    """Generates candidate plans from milestone context (Architecture_Final_Review_v1.3)."""

    async def generate_plan(
        self,
        milestone: Milestone,
        milestone_ctx: MilestoneContext,
        plan_attempts: list[dict[str, Any]],
        ctx: RunContext,
    ) -> ProposedPlan:
        """Return a proposed plan for the milestone."""
        ...
