from __future__ import annotations

from dare_framework.core.remediator.remediator import IRemediator
from dare_framework.core.context.models import MilestoneContext, RunContext
from dare_framework.core.plan.models import VerifyResult
from dare_framework.core.tool.models import ToolErrorRecord


class NoOpRemediator(IRemediator):
    async def remediate(
        self,
        verify_result: VerifyResult,
        tool_errors: list[ToolErrorRecord],
        milestone_ctx: MilestoneContext,
        ctx: RunContext,
    ) -> str:
        if not tool_errors and not verify_result.errors:
            return "no-op"
        combined = list(verify_result.errors) + [error.message for error in tool_errors]
        return "; ".join(combined)
