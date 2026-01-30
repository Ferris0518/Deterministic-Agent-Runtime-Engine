"""Fixtures for plan domain tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from dare_framework.context.kernel import IContext
from dare_framework.context.types import Budget, Message
from dare_framework.infra.component import ComponentType
from dare_framework.model.kernel import IModelAdapter
from dare_framework.model.types import GenerateOptions, ModelInput, ModelResponse
from dare_framework.plan.types import (
    Milestone,
    ProposedPlan,
    ProposedStep,
    Task,
)
from dare_framework.security.types import RiskLevel
from dare_framework.tool.interfaces import ITool
from dare_framework.tool.kernel import IToolGateway
from dare_framework.tool.types import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityMetadata,
    CapabilityType,
    ToolResult,
)


class MockContext(IContext):
    """Mock implementation of IContext for testing."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> None:
        self._config = config or {}
        self._messages: list[Message] = []
        self._toollist = tools or []
        self.budget = Budget()
        self.short_term_memory = MagicMock()
        self.long_term_memory = None
        self.knowledge = None
        self.toollist = self._toollist
        self.id = "ctx_test_001"

    def stm_add(self, message: Message) -> None:
        self._messages.append(message)

    def stm_get(self) -> list[Message]:
        return list(self._messages)

    def stm_clear(self) -> list[Message]:
        old = list(self._messages)
        self._messages.clear()
        return old

    def budget_use(self, resource: str, amount: float) -> None:
        setattr(self.budget, f"used_{resource}", amount)

    def budget_check(self) -> None:
        pass

    def budget_remaining(self, resource: str) -> float:
        limit = getattr(self.budget, f"max_{resource}", float("inf"))
        used = getattr(self.budget, f"used_{resource}", 0)
        return limit - used if limit else float("inf")

    def listing_tools(self) -> list[dict[str, Any]]:
        return self._toollist

    def assemble(self, **options: Any) -> Any:
        from dare_framework.context.types import AssembledContext

        return AssembledContext(
            messages=self._messages,
            tools=self._toollist,
            metadata={"options": options},
        )

    def config_update(self, patch: dict[str, Any]) -> None:
        self._config.update(patch)

    @property
    def config(self) -> dict[str, Any]:
        return self._config


class MockToolGateway(IToolGateway):
    """Mock implementation of IToolGateway for testing."""

    def __init__(self, capabilities: dict[str, CapabilityDescriptor] | None = None) -> None:
        self._capabilities = capabilities or {}
        self.invocations: list[tuple[str, dict[str, Any]]] = []

    async def list_capabilities(self) -> list[CapabilityDescriptor]:
        return list(self._capabilities.values())

    async def invoke(
        self, capability_id: str, params: dict[str, Any], *, envelope: Any
    ) -> Any:
        self.invocations.append((capability_id, params))
        return ToolResult(success=True, output={"invoked": capability_id})

    def register_provider(self, provider: object) -> None:
        pass

    def get_capability(
        self, capability_id: str, *, include_disabled: bool = False
    ) -> CapabilityDescriptor | None:
        return self._capabilities.get(capability_id)

    def add_capability(self, descriptor: CapabilityDescriptor) -> None:
        self._capabilities[descriptor.id] = descriptor


class MockModelAdapter(IModelAdapter):
    """Mock model adapter that returns predetermined responses."""

    def __init__(
        self,
        responses: list[str] | None = None,
        name: str = "mock_model",
    ) -> None:
        self._responses = responses or []
        self._response_index = 0
        self._name = name
        self.inputs: list[ModelInput] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def component_type(self) -> ComponentType:
        return ComponentType.MODEL_ADAPTER

    async def generate(
        self,
        model_input: ModelInput,
        *,
        options: GenerateOptions | None = None,
    ) -> ModelResponse:
        self.inputs.append(model_input)

        if self._response_index < len(self._responses):
            content = self._responses[self._response_index]
            self._response_index += 1
        else:
            content = '{}'

        return ModelResponse(content=content)


class MockTool(ITool):
    """Mock tool implementation."""

    def __init__(
        self,
        name: str,
        risk_level: RiskLevel = RiskLevel.READ_ONLY,
        input_schema: dict[str, Any] | None = None,
    ) -> None:
        self._name = name
        self._risk_level = risk_level
        self._input_schema = input_schema or {"type": "object", "properties": {}}

    @property
    def name(self) -> str:
        return self._name

    @property
    def component_type(self) -> ComponentType:
        return ComponentType.TOOL

    @property
    def description(self) -> str:
        return f"Mock tool: {self._name}"

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._input_schema

    @property
    def output_schema(self) -> dict[str, Any]:
        return {"type": "object"}

    @property
    def tool_type(self) -> str:
        from dare_framework.tool.types import ToolType

        return ToolType.ATOMIC.value

    @property
    def risk_level(self) -> str:
        return self._risk_level.value

    @property
    def requires_approval(self) -> bool:
        return self._risk_level in (
            RiskLevel.NON_IDEMPOTENT_EFFECT,
            RiskLevel.COMPENSATABLE,
        )

    @property
    def timeout_seconds(self) -> int:
        return 30

    @property
    def is_work_unit(self) -> bool:
        return False

    @property
    def capability_kind(self) -> CapabilityKind:
        return CapabilityKind.TOOL

    async def execute(self, input: dict[str, Any], context: Any) -> ToolResult:
        return ToolResult(success=True, output={"executed": self._name})


@pytest.fixture
def mock_context() -> MockContext:
    """Provide a mock context."""
    return MockContext()


@pytest.fixture
def mock_context_with_tools() -> MockContext:
    """Provide a mock context with sample tools."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "tool_read_file",
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                    },
                    "required": ["path"],
                },
            },
            "capability_id": "tool_read_file_001",
        },
        {
            "type": "function",
            "function": {
                "name": "tool_write_file",
                "description": "Write a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
            },
            "capability_id": "tool_write_file_001",
        },
    ]
    return MockContext(config={"task_description": "Test task"}, tools=tools)


@pytest.fixture
def mock_tool_gateway() -> MockToolGateway:
    """Provide a mock tool gateway with sample capabilities."""
    gateway = MockToolGateway()

    # Add read_file capability (read-only)
    gateway.add_capability(
        CapabilityDescriptor(
            id="tool_read_file_001",
            type=CapabilityType.TOOL,
            name="read_file",
            description="Read a file",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
            metadata=CapabilityMetadata(
                risk_level="read_only",
                requires_approval=False,
                capability_kind=CapabilityKind.TOOL,
            ),
        )
    )

    # Add write_file capability (idempotent write)
    gateway.add_capability(
        CapabilityDescriptor(
            id="tool_write_file_001",
            type=CapabilityType.TOOL,
            name="write_file",
            description="Write a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
            metadata=CapabilityMetadata(
                risk_level="idempotent_write",
                requires_approval=False,
                capability_kind=CapabilityKind.TOOL,
            ),
        )
    )

    return gateway


@pytest.fixture
def sample_task() -> Task:
    """Provide a sample task."""
    return Task(
        description="Test task",
        task_id="task_001",
    )


@pytest.fixture
def sample_milestone() -> Milestone:
    """Provide a sample milestone."""
    return Milestone(
        milestone_id="milestone_001",
        description="Test milestone",
        user_input="Do something useful",
    )


@pytest.fixture
def sample_proposed_plan() -> ProposedPlan:
    """Provide a sample proposed plan."""
    return ProposedPlan(
        plan_description="Test plan",
        steps=[
            ProposedStep(
                step_id="step_1",
                capability_id="tool_read_file_001",
                params={"path": "/test/file.txt"},
                description="Read the file",
            ),
        ],
        attempt=0,
    )
