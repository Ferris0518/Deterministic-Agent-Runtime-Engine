"""Default security boundary implementation."""

from __future__ import annotations

from vaf.security.component import ISecurityBoundary
from vaf.security.types import RiskLevel, PolicyDecision


class DefaultSecurityBoundary(ISecurityBoundary):
    """Default security boundary that allows all actions."""

    def check_policy(
        self,
        action: str,
        risk_level: RiskLevel,
    ) -> PolicyDecision:
        """Check if an action is allowed (default: allow all)."""
        return PolicyDecision.ALLOW
