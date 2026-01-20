"""Security domain facade (compat shim)."""

from dare_framework3.security.kernel import ISecurityBoundary
from dare_framework3.security.components import ITrustVerifier, IPolicyEngine, ISandbox
from dare_framework3.security.types import PolicyDecision, TrustedInput, SandboxSpec

__all__ = [
    "ISecurityBoundary",
    "ITrustVerifier",
    "IPolicyEngine",
    "ISandbox",
    "PolicyDecision",
    "TrustedInput",
    "SandboxSpec",
]
