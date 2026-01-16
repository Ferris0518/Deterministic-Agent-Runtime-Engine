from __future__ import annotations

from typing import Protocol

from dare_framework.core.context.models import MilestoneContext, RunContext
from dare_framework.core.plan.models import VerifyResult
from dare_framework.core.tool.models import ToolErrorRecord


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
