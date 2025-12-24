from __future__ import annotations

from typing import Iterable

from .interfaces import (
    IContextAssembler,
    IHook,
    IModelAdapter,
    IPlanGenerator,
    IPolicyEngine,
    IRemediator,
    IValidator,
)
from .models import (
    DonePredicate,
    Message,
    Milestone,
    PlanStep,
    ProposedPlan,
    RunContext,
    ToolResult,
    ValidationResult,
    VerifyResult,
    PolicyDecision,
    ToolRiskLevel,
)


class AllowAllPolicyEngine(IPolicyEngine):
    def check_tool_access(self, tool, ctx: RunContext) -> PolicyDecision:
        return PolicyDecision.ALLOW

    def needs_approval(self, milestone: Milestone, validated_plan) -> bool:
        return False


class SimpleValidator(IValidator):
    async def validate_plan(self, steps: list[PlanStep], ctx: RunContext) -> ValidationResult:
        if not steps:
            return ValidationResult(success=False, errors=["Plan has no steps"])
        return ValidationResult(success=True, errors=[])

    async def validate_milestone(self, milestone: Milestone, result, ctx: RunContext) -> VerifyResult:
        if result.success:
            return VerifyResult(success=True, errors=[], evidence={"milestone": milestone.milestone_id})
        return VerifyResult(success=False, errors=result.errors, evidence={})

    async def validate_evidence(self, evidence: dict, predicate: DonePredicate) -> bool:
        if not predicate.required_keys:
            return True
        return all(key in evidence for key in predicate.required_keys)


class NoOpRemediator(IRemediator):
    async def remediate(self, verify_result: VerifyResult, errors: list[str], ctx: RunContext) -> str:
        if not errors:
            return "no-op"
        return "; ".join(errors)


class BasicContextAssembler(IContextAssembler):
    async def assemble(self, milestone: Milestone, ctx: RunContext) -> list[Message]:
        return [Message(role="system", content=milestone.description)]

    async def compress(self, context: list[Message]) -> list[Message]:
        return context


class DeterministicPlanGenerator(IPlanGenerator):
    def __init__(self, plans: Iterable[list[PlanStep]]):
        self._plans = list(plans)

    async def generate_plan(self, milestone: Milestone, ctx: RunContext, attempt: int) -> ProposedPlan:
        index = min(attempt, len(self._plans) - 1)
        steps = self._plans[index] if self._plans else []
        return ProposedPlan(steps=steps, summary=milestone.description, attempt=attempt)


class MockModelAdapter(IModelAdapter):
    def __init__(self, responses: Iterable[str] | None = None):
        self._responses = list(responses or ["ok"])
        self._index = 0

    async def generate(self, messages: list[Message], tools) -> "ModelResponse":
        from .models import ModelResponse

        if not self._responses:
            return ModelResponse(content="")
        response = self._responses[min(self._index, len(self._responses) - 1)]
        self._index += 1
        return ModelResponse(content=response, tool_calls=[])


class NoOpHook(IHook):
    async def on_event(self, event) -> None:
        return None


class InMemoryMemory:
    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, text: str, metadata: dict | None = None) -> None:
        self._items.append(text)

    def search(self, query: str, limit: int = 5) -> list[str]:
        if not query:
            return self._items[:limit]
        return [item for item in self._items if query in item][:limit]


class NoOpTool:
    @property
    def name(self) -> str:
        return "noop"

    @property
    def description(self) -> str:
        return "No-op tool for default runtime wiring."

    @property
    def input_schema(self) -> dict:
        return {"type": "object", "properties": {}}

    @property
    def output_schema(self) -> dict:
        return {"type": "object", "properties": {"status": {"type": "string"}}}

    @property
    def risk_level(self):
        return ToolRiskLevel.READ_ONLY

    @property
    def requires_approval(self) -> bool:
        return False

    @property
    def timeout_seconds(self) -> int:
        return 5

    @property
    def produces_assertions(self) -> list[dict]:
        return []

    @property
    def is_work_unit(self) -> bool:
        return False

    async def execute(self, input: dict, context: RunContext) -> ToolResult:
        return ToolResult(success=True, output={"status": "ok"}, evidence={})
