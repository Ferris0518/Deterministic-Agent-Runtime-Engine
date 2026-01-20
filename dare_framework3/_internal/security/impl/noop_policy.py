"""No-op policy engine implementation."""

from __future__ import annotations

from dare_framework3._internal.security.components import IPolicyEngine
from dare_framework3._internal.security.types import PolicyDecision


class NoOpPolicyEngine(IPolicyEngine):
    """Policy engine that always allows actions."""

    async def check_policy(
        self,
        *,
        action: str,
        resource: str,
        context: dict[str, object],
    ) -> PolicyDecision:
        _ = (action, resource, context)
        return PolicyDecision.ALLOW
