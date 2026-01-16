from __future__ import annotations

from typing import Protocol, runtime_checkable

from dare_framework.core.configurable_component import IConfigurableComponent
from dare_framework.core.context.models import AssembledContext, MemoryItem, MilestoneContext, RunContext, RuntimeSnapshot
from dare_framework.core.plan.models import Milestone, ProposedPlan, ProposedStep, ValidatedPlan, ValidatedStep
from dare_framework.core.tool.enums import PolicyDecision
from dare_framework.core.tool.protocols import ITool, IToolRegistry


class ICheckpoint(Protocol):
    """Snapshot storage for runtime state across context windows (Architecture_Final_Review_v1.3)."""

    async def save(self, snapshot: RuntimeSnapshot) -> str:
        """Persist a runtime snapshot and return checkpoint id."""
        ...

    async def load(self, checkpoint_id: str) -> RuntimeSnapshot:
        """Load a previously saved runtime snapshot."""
        ...


class IContextAssembler(Protocol):
    """Assembles and compresses runtime context (Architecture_Final_Review_v1.3)."""

    async def assemble(
        self,
        milestone: Milestone,
        milestone_ctx: MilestoneContext,
        ctx: RunContext,
    ) -> AssembledContext:
        """Build an assembled context for the milestone."""
        ...

    async def compress(self, context: AssembledContext, max_tokens: int) -> AssembledContext:
        """Compress assembled context to meet token limits."""
        ...


@runtime_checkable
class IMemory(IConfigurableComponent, Protocol):
    """Memory storage and retrieval (Interface_Layer_Design_v1.1)."""

    async def store(self, key: str, value: str, metadata: dict | None = None) -> None:
        """Persist a memory entry."""
        ...

    async def search(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        """Search for relevant memories by query."""
        ...

    async def get(self, key: str) -> str | None:
        """Retrieve a stored memory by key."""
        ...


class IPolicyEngine(Protocol):
    """Policy enforcement for tool access and approval gates (Architecture_Final_Review_v1.3)."""

    def check_tool_access(self, tool: ITool, ctx: RunContext) -> PolicyDecision:
        """Evaluate a tool invocation against policy rules."""
        ...

    def needs_approval(self, milestone: Milestone, validated_plan: ValidatedPlan) -> bool:
        """Determine whether the validated plan requires human approval."""
        ...

    def enforce(self, action: str, resource: str, ctx: RunContext) -> None:
        """Enforce policy for arbitrary actions/resources."""
        ...


class ITrustBoundary(Protocol):
    """Derives trusted fields before policy enforcement (Architecture_Final_Review_v1.3)."""

    def derive_step(self, proposed_step: ProposedStep, registry: IToolRegistry) -> ValidatedStep:
        """Return a validated step derived from trusted tool metadata."""
        ...

    def derive_plan(self, proposed_plan: ProposedPlan, registry: IToolRegistry) -> ValidatedPlan:
        """Return a validated plan derived from trusted tool metadata."""
        ...

