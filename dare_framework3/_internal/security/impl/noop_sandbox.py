"""No-op sandbox implementation."""

from __future__ import annotations

from typing import Any, Callable

from dare_framework3._internal.security.components import ISandbox
from dare_framework3._internal.security.types import SandboxSpec


class NoOpSandbox(ISandbox):
    """Sandbox that executes functions directly."""

    async def execute(
        self,
        *,
        action: str,
        fn: Callable[[], Any],
        sandbox: SandboxSpec,
    ) -> Any:
        _ = (action, sandbox)
        return fn()
