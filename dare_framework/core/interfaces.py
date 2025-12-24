from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, TypeVar
from typing import TYPE_CHECKING

from dare_framework.core.events import Event, EventFilter, EventID
from dare_framework.core.models import (
    AssembledContext,
    DonePredicate,
    Envelope,
    Evidence,
    ExecuteResult,
    Milestone,
    MilestoneContext,
    ProposedPlan,
    ProposedStep,
    RunContext,
    RunResult,
    Task,
    ToolDefinition,
    ToolResult,
    ToolError,
    ValidationResult,
    ValidatedPlan,
    VerifyResult,
)
from dare_framework.core.state import RuntimeState

if TYPE_CHECKING:
    from dare_framework.components.layer2 import ISkill, ITool

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVE_REQUIRED = "approve_required"


class IRuntime(Protocol[DepsT, OutputT]):
    async def init(self, task: Task) -> None:
        ...

    async def run(self, task: Task, deps: DepsT) -> RunResult[OutputT]:
        ...

    async def pause(self) -> None:
        ...

    async def resume(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def cancel(self) -> None:
        ...

    def get_state(self) -> RuntimeState:
        ...


class IEventLog(Protocol):
    async def append(self, event: Event) -> EventID:
        ...

    async def query(
        self,
        filter: EventFilter | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Event]:
        ...

    async def verify_chain(self) -> bool:
        ...

    async def get_checkpoint_events(self, checkpoint_id: str) -> list[Event]:
        ...


class IToolRuntime(Protocol):
    async def invoke(
        self,
        name: str,
        input: dict[str, Any],
        ctx: RunContext,
        envelope: Envelope | None = None,
        done_predicate: DonePredicate | None = None,
    ) -> ToolResult:
        ...

    def get_tool(self, name: str) -> ITool | None:
        ...

    def list_tools(self) -> list[ToolDefinition]:
        ...

    def is_plan_tool(self, name: str) -> bool:
        ...


class IPolicyEngine(Protocol):
    def check_tool_access(self, tool: ITool, ctx: RunContext) -> PolicyDecision:
        ...

    def needs_approval(self, milestone: Milestone, validated_plan: ValidatedPlan) -> bool:
        ...

    def enforce(self, action: str, resource: str, ctx: RunContext) -> None:
        ...


class IPlanGenerator(Protocol):
    async def generate_plan(
        self,
        milestone: Milestone,
        milestone_ctx: MilestoneContext,
        plan_attempts: list[dict[str, Any]],
        ctx: RunContext,
    ) -> ProposedPlan:
        ...


class IValidator(Protocol):
    async def validate_plan(
        self,
        proposed_steps: list[ProposedStep],
        ctx: RunContext,
    ) -> ValidationResult:
        ...

    async def validate_milestone(
        self,
        milestone: Milestone,
        execute_result: ExecuteResult,
        ctx: RunContext,
    ) -> VerifyResult:
        ...

    async def validate_evidence(self, evidence: list[Evidence], predicate: DonePredicate) -> bool:
        ...


class IRemediator(Protocol):
    async def remediate(
        self,
        verify_result: VerifyResult,
        tool_errors: list[ToolError],
        milestone_ctx: MilestoneContext,
        ctx: RunContext,
    ) -> str:
        ...


class ISkillRegistry(Protocol):
    def register_skill(self, skill: ISkill) -> None:
        ...

    def get_skill(self, name: str) -> ISkill | None:
        ...

    def list_skills(self) -> list[ISkill]:
        ...


class IContextAssembler(Protocol):
    async def assemble(
        self,
        milestone: Milestone,
        milestone_ctx: MilestoneContext,
        ctx: RunContext,
    ) -> AssembledContext:
        ...

    async def compress(self, context: AssembledContext, max_tokens: int) -> AssembledContext:
        ...
