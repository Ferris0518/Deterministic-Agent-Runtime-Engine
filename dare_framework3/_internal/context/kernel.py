"""Context domain kernel interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from dare_framework3._internal.context.types import (
    AssembledContext,
    ContextPacket,
    ContextStage,
    IndexStatus,
    RetrievedContext,
    RuntimeStateView,
    SessionContext,
)

if TYPE_CHECKING:
    from dare_framework3._internal.plan.types import Task
    from dare_framework3._internal.execution.types import Budget


class IContextManager(Protocol):
    """Context engineering responsibility owner."""

    def open_session(self, task: "Task") -> SessionContext:
        ...

    async def assemble(
        self,
        stage: ContextStage,
        state: RuntimeStateView,
    ) -> AssembledContext:
        ...

    async def retrieve(
        self,
        query: str,
        *,
        budget: "Budget",
    ) -> RetrievedContext:
        ...

    async def ensure_index(self, scope: str) -> IndexStatus:
        ...

    async def compress(
        self,
        context: AssembledContext,
        *,
        budget: "Budget",
    ) -> AssembledContext:
        ...

    async def route(self, packet: ContextPacket, target: str) -> None:
        ...
