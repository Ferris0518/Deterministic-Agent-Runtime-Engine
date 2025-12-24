from __future__ import annotations

from ..core.interfaces import IContextAssembler
from ..core.models import Message, Milestone, RunContext


class BasicContextAssembler(IContextAssembler):
    async def assemble(self, milestone: Milestone, ctx: RunContext) -> list[Message]:
        return [Message(role="system", content=milestone.description)]

    async def compress(self, context: list[Message]) -> list[Message]:
        return context
