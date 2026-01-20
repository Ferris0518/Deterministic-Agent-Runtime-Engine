"""Protocol adapter interfaces (Layer 1)."""

from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable

from dare_framework3._internal.tool.types import CapabilityDescriptor


@runtime_checkable
class IProtocolAdapter(Protocol):
    """Protocol adapter contract (Layer 1)."""

    @property
    def protocol_name(self) -> str:
        ...

    async def connect(self, endpoint: str, config: dict[str, Any]) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    async def discover(self) -> Sequence[CapabilityDescriptor]:
        ...

    async def invoke(
        self,
        capability_id: str,
        params: dict[str, Any],
        *,
        timeout: float | None = None,
    ) -> Any:
        ...
