"""Security domain component interfaces."""

from __future__ import annotations

from typing import Protocol

from vaf.security.types import RiskLevel, PolicyDecision


class ISecurityBoundary(Protocol):
    """Security boundary interface.
    
    Checks policies and risk levels for tool execution.
    """

    def check_policy(
        self,
        action: str,
        risk_level: RiskLevel,
    ) -> PolicyDecision:
        """Check if an action is allowed.
        
        Args:
            action: The action to check
            risk_level: The risk level of the action
            
        Returns:
            Policy decision (ALLOW, DENY, or APPROVE_REQUIRED)
        """
        ...
