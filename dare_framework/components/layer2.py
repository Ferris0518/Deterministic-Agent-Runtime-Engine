from __future__ import annotations

from typing import Any, AsyncIterator, Generic, Protocol, TypeVar

from dare_framework.core.models import (
    DonePredicate,
    Envelope,
    GenerateOptions,
    MemoryItem,
    Message,
    Milestone,
    ModelResponse,
    RunContext,
    RunResult,
    Task,
    ToolDefinition,
    ToolResult,
    RiskLevel,
    ToolType,
    MilestoneSummary,
    SessionSummary,
)
from dare_framework.core.state import RuntimeState

T = TypeVar("T")


class IModelAdapter(Protocol):
    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        options: GenerateOptions | None = None,
    ) -> ModelResponse:
        ...

    async def generate_structured(
        self,
        messages: list[Message],
        output_schema: type[Any],
    ) -> Any:
        ...


class IMemory(Protocol):
    async def store(self, key: str, value: str, metadata: dict | None = None) -> None:
        ...

    async def search(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        ...

    async def get(self, key: str) -> str | None:
        ...


class ITool(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def tool_type(self) -> ToolType:
        ...

    @property
    def risk_level(self) -> RiskLevel:
        ...

    def get_input_schema(self) -> dict[str, Any]:
        ...

    async def execute(self, input: dict[str, Any], ctx: RunContext) -> ToolResult:
        ...


class ISkill(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    def get_envelope(self, input: dict[str, Any]) -> Envelope:
        ...

    def get_done_predicate(self, input: dict[str, Any]) -> DonePredicate:
        ...

    def get_input_schema(self) -> dict[str, Any]:
        ...


class IToolkit(Protocol):
    def register_tool(self, tool: ITool) -> None:
        ...

    def get_tool(self, name: str) -> ITool | None:
        ...

    def list_tools(self) -> list[ITool]:
        ...

    def activate_group(self, group_name: str) -> None:
        ...


class IMCPClient(Protocol):
    async def connect(self, server_config: dict[str, Any]) -> None:
        ...

    async def list_tools(self) -> list[dict[str, Any]]:
        ...

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        ...

    async def disconnect(self) -> None:
        ...


class IHook(Protocol):
    async def on_session_start(self, task: Task) -> None:
        ...

    async def on_milestone_start(self, milestone: Milestone) -> None:
        ...

    async def on_tool_call(self, tool_name: str, input: dict[str, Any], result: ToolResult) -> None:
        ...

    async def on_session_end(self, result: RunResult[Any]) -> None:
        ...


class ICheckpoint(Protocol):
    async def save(self, task_id: str, state: RuntimeState, milestone_id: str | None = None) -> str:
        ...

    async def load(self, checkpoint_id: str) -> RuntimeState:
        ...

    async def save_milestone_summary(
        self,
        milestone_id: str,
        summary: MilestoneSummary,
    ) -> None:
        ...

    async def load_milestone_summary(self, milestone_id: str) -> MilestoneSummary:
        ...

    async def is_completed(self, milestone_id: str) -> bool:
        ...

    async def save_session_summary(self, summary: SessionSummary) -> None:
        ...

    async def load_session_summary(self, session_id: str) -> SessionSummary | None:
        ...


class IStreamedResponse(Protocol, Generic[T]):
    async def __aiter__(self) -> AsyncIterator[T]:
        ...
