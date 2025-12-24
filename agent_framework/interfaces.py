from __future__ import annotations

from typing import Any, Generic, Protocol, TypeVar

from .models import (
    Event,
    EventFilter,
    Message,
    Milestone,
    ModelResponse,
    PlanStep,
    ProposedPlan,
    RunContext,
    RunResult,
    RuntimeSnapshot,
    RuntimeState,
    ToolDefinition,
    ToolResult,
    ValidationResult,
    VerifyResult,
    PolicyDecision,
)

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


class IRuntime(Protocol, Generic[DepsT, OutputT]):
    async def init(self, task: "Task") -> None:
        ...

    async def run(self, task: "Task", deps: DepsT) -> RunResult[OutputT]:
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
    async def append(self, event: Event) -> str:
        ...

    async def query(self, filter: EventFilter | None = None, offset: int = 0, limit: int = 100) -> list[Event]:
        ...

    async def verify_chain(self) -> bool:
        ...

    async def get_checkpoint_events(self, checkpoint_id: str) -> list[Event]:
        ...


class ICheckpoint(Protocol):
    async def save(self, snapshot: RuntimeSnapshot) -> str:
        ...

    async def load(self, checkpoint_id: str) -> RuntimeSnapshot:
        ...


class ITool(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def input_schema(self) -> dict[str, Any]:
        ...

    @property
    def output_schema(self) -> dict[str, Any]:
        ...

    @property
    def risk_level(self):
        ...

    @property
    def requires_approval(self) -> bool:
        ...

    @property
    def timeout_seconds(self) -> int:
        ...

    @property
    def produces_assertions(self) -> list[dict[str, Any]]:
        ...

    @property
    def is_work_unit(self) -> bool:
        ...

    async def execute(self, input: dict[str, Any], context: RunContext) -> ToolResult:
        ...


class IToolkit(Protocol):
    def register_tool(self, tool: ITool) -> None:
        ...

    def get_tool(self, name: str) -> ITool | None:
        ...

    def list_tools(self) -> list[ToolDefinition]:
        ...


class ISkill(Protocol):
    @property
    def name(self) -> str:
        ...

    async def execute(self, input: dict[str, Any], context: RunContext) -> ToolResult:
        ...


class ISkillRegistry(Protocol):
    def register_skill(self, skill: ISkill) -> None:
        ...

    def get_skill(self, name: str) -> ISkill | None:
        ...

    def list_skills(self) -> list[ISkill]:
        ...


class IToolRuntime(Protocol):
    async def invoke(
        self,
        name: str,
        input: dict[str, Any],
        ctx: RunContext,
        envelope: "Envelope | None" = None,
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

    def needs_approval(self, milestone: Milestone, validated_plan: "ValidatedPlan") -> bool:
        ...


class IPlanGenerator(Protocol):
    async def generate_plan(
        self,
        milestone: Milestone,
        ctx: RunContext,
        attempt: int,
    ) -> ProposedPlan:
        ...


class IValidator(Protocol):
    async def validate_plan(self, steps: list[PlanStep], ctx: RunContext) -> ValidationResult:
        ...

    async def validate_milestone(
        self,
        milestone: Milestone,
        result: "ExecuteResult",
        ctx: RunContext,
    ) -> VerifyResult:
        ...

    async def validate_evidence(self, evidence: dict[str, Any], predicate: "DonePredicate") -> bool:
        ...


class IRemediator(Protocol):
    async def remediate(self, verify_result: VerifyResult, errors: list[str], ctx: RunContext) -> str:
        ...


class IContextAssembler(Protocol):
    async def assemble(self, milestone: Milestone, ctx: RunContext) -> list[Message]:
        ...

    async def compress(self, context: list[Message]) -> list[Message]:
        ...


class IModelAdapter(Protocol):
    async def generate(self, messages: list[Message], tools: list[ToolDefinition]) -> ModelResponse:
        ...


class IMemory(Protocol):
    def add(self, text: str, metadata: dict[str, Any] | None = None) -> None:
        ...

    def search(self, query: str, limit: int = 5) -> list[str]:
        ...


class IHook(Protocol):
    async def on_event(self, event: Event) -> None:
        ...


class IMCPClient(Protocol):
    @property
    def name(self) -> str:
        ...

    async def connect(self) -> None:
        ...

    async def list_tools(self) -> list[ToolDefinition]:
        ...

    async def call_tool(self, name: str, input: dict[str, Any]) -> ToolResult:
        ...

    async def list_resources(self) -> list[str]:
        ...


class IAgent(Protocol, Generic[DepsT, OutputT]):
    async def run(self, task: "Task", deps: DepsT) -> RunResult[OutputT]:
        ...


from .models import (
    DonePredicate,
    Envelope,
    ExecuteResult,
    Task,
    ValidatedPlan,
)
