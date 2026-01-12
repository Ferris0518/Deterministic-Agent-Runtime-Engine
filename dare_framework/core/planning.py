from __future__ import annotations

from typing import Any, Protocol

from .models.context import MilestoneContext
from .models.plan import Milestone, ProposedPlan, VerifyResult
from .models.runtime import RunContext
from .models.tool import ToolErrorRecord


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


class IRemediator(Protocol):
    """Derives remediation directives when validation fails (Architecture_Final_Review_v1.3)."""

    async def remediate(
        self,
        verify_result: VerifyResult,
        tool_errors: list[ToolErrorRecord],
        milestone_ctx: MilestoneContext,
        ctx: RunContext,
    ) -> str:
        """Generate remediation guidance for the next plan attempt."""
        ...
