from __future__ import annotations

from ..core.policy import IPolicyEngine
from ..core.models.plan import Milestone, ValidatedPlan
from ..core.models.runtime import RunContext
from ..core.models.tool import PolicyDecision


class AllowAllPolicyEngine(IPolicyEngine):
    def check_tool_access(self, tool, ctx: RunContext) -> PolicyDecision:
        return PolicyDecision.ALLOW

    def needs_approval(self, milestone: Milestone, validated_plan: ValidatedPlan) -> bool:
        return False

    def enforce(self, action: str, resource: str, ctx: RunContext) -> None:
        return None
