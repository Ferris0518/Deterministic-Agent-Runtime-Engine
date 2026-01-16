from __future__ import annotations

from dare_framework.core.context.protocols import IContextAssembler
from dare_framework.core.models.prompt_store import IPromptStore
from dare_framework.core.context.models import AssembledContext, MilestoneContext, RunContext
from dare_framework.core.models.model_adapter import Message
from dare_framework.core.plan.models import Milestone
from dare_framework.core.models.prompts import BASE_SYSTEM_PROMPT, BASE_SYSTEM_PROMPT_NAME


class BasicContextAssembler(IContextAssembler):
    def __init__(self, prompt_store: IPromptStore | None = None) -> None:
        self._prompt_store = prompt_store

    def _get_base_prompt(self) -> str:
        if self._prompt_store is None:
            return BASE_SYSTEM_PROMPT
        try:
            return self._prompt_store.get_prompt(BASE_SYSTEM_PROMPT_NAME)
        except KeyError:
            return BASE_SYSTEM_PROMPT

    async def assemble(
        self,
        milestone: Milestone,
        milestone_ctx: MilestoneContext,
        ctx: RunContext,
    ) -> AssembledContext:
        messages = [
            Message(role="system", content=self._get_base_prompt()),
            Message(role="user", content=milestone_ctx.user_input),
        ]
        return AssembledContext(messages=messages)

    async def compress(self, context: AssembledContext, max_tokens: int) -> AssembledContext:
        return context
