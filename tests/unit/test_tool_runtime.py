import pytest

from dare_framework.components import AllowAllPolicy, BasicToolkit
from dare_framework.components.registries import SkillRegistry
from dare_framework.components.tool_runtime import DefaultToolRuntime
from dare_framework.core.errors import ToolExecutionError
from dare_framework.core.models import (
    DonePredicate,
    Envelope,
    EnvelopeBudget,
    Evidence,
    EvidenceCondition,
    RiskLevel,
    RunContext,
    ToolResult,
    ToolType,
)


class CounterTool:
    def __init__(self) -> None:
        self.count = 0

    @property
    def name(self) -> str:
        return "counter"

    @property
    def description(self) -> str:
        return "Counts tool invocations."

    @property
    def tool_type(self) -> ToolType:
        return ToolType.WORKUNIT

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.READ_ONLY

    def get_input_schema(self) -> dict:
        return {"type": "object", "properties": {}}

    async def execute(self, input: dict, ctx: RunContext) -> ToolResult:
        self.count += 1
        kind = "done" if self.count >= 2 else "partial"
        evidence = Evidence(evidence_id=f"e{self.count}", kind=kind, payload={})
        return ToolResult(success=True, output={"count": self.count}, evidence_ref=evidence)


class DummySkill:
    @property
    def name(self) -> str:
        return "fix_bug"

    @property
    def description(self) -> str:
        return "Dummy skill"

    def get_input_schema(self) -> dict:
        return {"type": "object", "properties": {}}

    def get_envelope(self, input: dict):
        return Envelope(
            allowed_tools=[],
            required_evidence=[],
            budget=EnvelopeBudget(),
            risk_level=RiskLevel.READ_ONLY,
        )

    def get_done_predicate(self, input: dict):
        return DonePredicate(
            evidence_conditions=[],
            invariant_conditions=[],
        )


@pytest.mark.asyncio
async def test_tool_runtime_plan_tool_detection():
    toolkit = BasicToolkit()
    skill_registry = SkillRegistry()
    skill_registry.register_skill(DummySkill())

    runtime = DefaultToolRuntime(
        toolkit,
        AllowAllPolicy(),
        skill_registry=skill_registry,
    )

    assert runtime.is_plan_tool("fix_bug") is True
    definitions = runtime.list_tools()
    assert any(tool.name == "fix_bug" and tool.is_plan_tool for tool in definitions)


@pytest.mark.asyncio
async def test_tool_runtime_workunit_done_predicate():
    tool = CounterTool()
    toolkit = BasicToolkit()
    toolkit.register_tool(tool)

    runtime = DefaultToolRuntime(toolkit, AllowAllPolicy())

    envelope = Envelope(
        allowed_tools=[],
        required_evidence=[],
        budget=EnvelopeBudget(max_tool_calls=3),
        risk_level=RiskLevel.READ_ONLY,
    )
    predicate = DonePredicate(
        evidence_conditions=[
            EvidenceCondition(condition_type="evidence_kind", params={"kind": "done"})
        ],
        invariant_conditions=[],
    )

    result = await runtime.invoke(
        "counter",
        {},
        RunContext(None, "r1"),
        envelope=envelope,
        done_predicate=predicate,
    )

    assert result.success is True
    assert tool.count == 2


@pytest.mark.asyncio
async def test_tool_runtime_workunit_budget_exceeded():
    tool = CounterTool()
    toolkit = BasicToolkit()
    toolkit.register_tool(tool)

    runtime = DefaultToolRuntime(toolkit, AllowAllPolicy())

    envelope = Envelope(
        allowed_tools=[],
        required_evidence=[],
        budget=EnvelopeBudget(max_tool_calls=1),
        risk_level=RiskLevel.READ_ONLY,
    )
    predicate = DonePredicate(
        evidence_conditions=[
            EvidenceCondition(condition_type="evidence_kind", params={"kind": "done"})
        ],
        invariant_conditions=[],
    )

    with pytest.raises(ToolExecutionError):
        await runtime.invoke(
            "counter",
            {},
            RunContext(None, "r1"),
            envelope=envelope,
            done_predicate=predicate,
        )
