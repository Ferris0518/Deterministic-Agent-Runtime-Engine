"""Security domain kernel interfaces."""

from __future__ import annotations

from typing import Any, Callable, Protocol

from dare_framework3._internal.security.types import PolicyDecision, SandboxSpec, TrustedInput


class ISecurityBoundary(Protocol):
    """Trust + policy + sandbox boundary."""

    async def verify_trust(
        self,
        *,
        input: dict[str, Any],
        context: dict[str, Any],
    ) -> TrustedInput:
        ...

    async def check_policy(
        self,
        *,
        action: str,
        resource: str,
        context: dict[str, Any],
    ) -> PolicyDecision:
        ...

    async def execute_safe(
        self,
        *,
        action: str,
        fn: Callable[[], Any],
        sandbox: SandboxSpec,
    ) -> Any:
        ...
