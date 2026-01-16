from __future__ import annotations

from dare_framework.core.context.models import RunContext
from dare_framework.core.context.protocols import IPolicyEngine
from dare_framework.core.plan.models import Milestone, ValidatedPlan
from dare_framework.core.tool.enums import PolicyDecision


class AllowAllPolicyEngine(IPolicyEngine):
    def check_tool_access(self, tool, ctx: RunContext) -> PolicyDecision:
        return PolicyDecision.ALLOW

    def needs_approval(self, milestone: Milestone, validated_plan: ValidatedPlan) -> bool:
        return False

    def enforce(self, action: str, resource: str, ctx: RunContext) -> None:
        return None
