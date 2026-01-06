from __future__ import annotations

from ..core.planning import IRemediator
from ..core.models.context import MilestoneContext
from ..core.models.plan import VerifyResult
from ..core.models.runtime import RunContext
from ..core.models.tool import ToolErrorRecord


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
