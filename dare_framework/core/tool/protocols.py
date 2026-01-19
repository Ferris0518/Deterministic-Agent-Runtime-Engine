"""Kernel tool gateway protocols (v2)."""

from __future__ import annotations

from typing import Any, Protocol, Sequence

from dare_framework.core.plan.envelope import Envelope
from dare_framework.core.tool.models import CapabilityDescriptor


class ICapabilityProvider(Protocol):
    """Provides capabilities to the Kernel tool gateway (Layer 2/1 integration)."""

    async def list(self) -> list[CapabilityDescriptor]: ...

    async def invoke(self, capability_id: str, params: dict[str, Any]) -> object: ...


class IToolGateway(Protocol):
    """System call boundary and unified invocation entry (v2.0)."""

    async def list_capabilities(self) -> Sequence[CapabilityDescriptor]: ...

    async def invoke(self, capability_id: str, params: dict[str, Any], *, envelope: Envelope) -> Any: ...

    def register_provider(self, provider: ICapabilityProvider) -> None: ...
