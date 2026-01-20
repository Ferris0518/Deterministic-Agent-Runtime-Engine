"""Security component interfaces (compat shim)."""

from dare_framework3._internal.security.components import ITrustVerifier, IPolicyEngine, ISandbox

__all__ = ["ITrustVerifier", "IPolicyEngine", "ISandbox"]
