from __future__ import annotations

from typing import Protocol

from .models.plan import Milestone, ValidatedPlan
from .models.runtime import RunContext
from .models.tool import PolicyDecision
from .tooling import ITool


class IPolicyEngine(Protocol):
    """Policy enforcement for tool access and approval gates (Architecture_Final_Review_v1.3)."""

    def check_tool_access(self, tool: ITool, ctx: RunContext) -> PolicyDecision:
        """Evaluate a tool invocation against policy rules."""
        ...

    def needs_approval(self, milestone: Milestone, validated_plan: ValidatedPlan) -> bool:
        """Determine whether the validated plan requires human approval."""
        ...

    def enforce(self, action: str, resource: str, ctx: RunContext) -> None:
        """Enforce policy for arbitrary actions/resources."""
        ...
