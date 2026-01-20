"""Security domain: Security boundary interfaces and types."""

from vaf.security.component import ISecurityBoundary
from vaf.security.types import RiskLevel, PolicyDecision
from vaf.security.impl.default_security_boundary import DefaultSecurityBoundary

__all__ = [
    "ISecurityBoundary",
    "RiskLevel",
    "PolicyDecision",
    "DefaultSecurityBoundary",
]
