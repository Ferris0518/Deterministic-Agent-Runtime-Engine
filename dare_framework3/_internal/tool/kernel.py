"""Tool domain kernel interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, Sequence

from dare_framework3._internal.tool.components import ICapabilityProvider
from dare_framework3._internal.tool.types import CapabilityDescriptor

if TYPE_CHECKING:
    from dare_framework3._internal.plan.types import Envelope


class IToolGateway(Protocol):
    """System call boundary and unified invocation entry."""

    async def list_capabilities(self) -> Sequence[CapabilityDescriptor]:
        ...

    async def invoke(
        self,
        capability_id: str,
        params: dict[str, Any],
        *,
        envelope: "Envelope",
    ) -> Any:
        ...

    def register_provider(self, provider: ICapabilityProvider) -> None:
        ...
