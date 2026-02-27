from __future__ import annotations

from typing import Any

import pytest

from dare_framework.agent.dare_agent import DareAgent
from dare_framework.config import Config
from dare_framework.context import Context
from dare_framework.plan.types import ProposedPlan, Task, ToolLoopRequest, ValidatedPlan
from dare_framework.security import PolicyDecision, RiskLevel, TrustedInput
from dare_framework.tool.types import ToolResult


class _RecordingModel:
    name = "recording-model"

    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, model_input: Any, *, options: Any = None) -> Any:
        _ = (model_input, options)
        self.calls += 1
        from dare_framework.model.types import ModelResponse

        return ModelResponse(content="ok", tool_calls=[])


class _RecordingToolGateway:
    def __init__(self) -> None:
        self.invoke_calls = 0
        self.last_params: dict[str, Any] | None = None

    def list_capabilities(self) -> list[Any]:
        return []

    async def invoke(self, capability_id: str, *, envelope: Any, **params: Any) -> ToolResult[dict[str, Any]]:
        _ = (capability_id, envelope)
        self.invoke_calls += 1
        self.last_params = dict(params)
        return ToolResult(success=True, output={"ok": True})


class _AllowBoundary:
    async def verify_trust(self, *, input: dict[str, Any], context: dict[str, Any]) -> TrustedInput:
        _ = context
        return TrustedInput(params=dict(input), risk_level=RiskLevel.READ_ONLY)

    async def check_policy(self, *, action: str, resource: str, context: dict[str, Any]) -> PolicyDecision:
        _ = (action, resource, context)
        return PolicyDecision.ALLOW

    async def execute_safe(self, *, action: str, fn: Any, sandbox: Any) -> Any:
        _ = (action, sandbox)
        value = fn()
        if hasattr(value, "__await__"):
            return await value
        return value


class _DenyToolBoundary(_AllowBoundary):
    async def check_policy(self, *, action: str, resource: str, context: dict[str, Any]) -> PolicyDecision:
        _ = (resource, context)
        if action == "invoke_tool":
            return PolicyDecision.DENY
        return PolicyDecision.ALLOW


class _ApproveToolBoundary(_AllowBoundary):
    async def check_policy(self, *, action: str, resource: str, context: dict[str, Any]) -> PolicyDecision:
        _ = (resource, context)
        if action == "invoke_tool":
            return PolicyDecision.APPROVE_REQUIRED
        return PolicyDecision.ALLOW


class _TrustRewriteBoundary(_AllowBoundary):
    async def verify_trust(self, *, input: dict[str, Any], context: dict[str, Any]) -> TrustedInput:
        _ = (input, context)
        return TrustedInput(
            params={"trusted": "yes"},
            risk_level=RiskLevel.IDEMPOTENT_WRITE,
            metadata={"source": "policy"},
        )


class _PlanDenyBoundary(_AllowBoundary):
    async def check_policy(self, *, action: str, resource: str, context: dict[str, Any]) -> PolicyDecision:
        _ = (resource, context)
        if action == "execute_plan":
            return PolicyDecision.DENY
        return PolicyDecision.ALLOW


class _Planner:
    async def plan(self, ctx: Any) -> ProposedPlan:
        _ = ctx
        return ProposedPlan(plan_description="plan", steps=[], attempt=1)

    async def decompose(self, task: Task, ctx: Any) -> Any:
        _ = ctx
        from dare_framework.plan.types import DecompositionResult

        return DecompositionResult(
            milestones=task.to_milestones(),
            reasoning="unit-test decomposition",
        )


class _Validator:
    async def validate_plan(self, plan: ProposedPlan, ctx: Any) -> ValidatedPlan:
        _ = (plan, ctx)
        return ValidatedPlan(success=True, plan_description="validated", steps=[])

    async def verify_milestone(self, result: Any, ctx: Any, *, plan: ValidatedPlan | None = None) -> Any:
        _ = (result, ctx, plan)
        from dare_framework.plan.types import VerifyResult

        return VerifyResult(success=True)


def _build_agent(
    *,
    boundary: Any,
    model: _RecordingModel | None = None,
    planner: Any | None = None,
    validator: Any | None = None,
    tool_gateway: _RecordingToolGateway | None = None,
) -> DareAgent:
    return DareAgent(
        name="security-agent",
        model=model or _RecordingModel(),
        context=Context(config=Config()),
        tool_gateway=tool_gateway or _RecordingToolGateway(),
        planner=planner,
        validator=validator,
        security_boundary=boundary,
    )


@pytest.mark.asyncio
async def test_tool_loop_denied_by_security_policy() -> None:
    tool_gateway = _RecordingToolGateway()
    agent = _build_agent(boundary=_DenyToolBoundary(), tool_gateway=tool_gateway)

    result = await agent._run_tool_loop(  # noqa: SLF001
        ToolLoopRequest(capability_id="tool.echo", params={"value": 1}),
        tool_name="echo",
        tool_call_id="tc-security-deny",
    )

    assert result["success"] is False
    assert "security policy" in str(result["error"])
    assert tool_gateway.invoke_calls == 0


@pytest.mark.asyncio
async def test_tool_loop_approve_required_without_execution_control_fails() -> None:
    tool_gateway = _RecordingToolGateway()
    agent = _build_agent(boundary=_ApproveToolBoundary(), tool_gateway=tool_gateway)

    result = await agent._run_tool_loop(  # noqa: SLF001
        ToolLoopRequest(capability_id="tool.echo", params={"value": 1}),
        tool_name="echo",
        tool_call_id="tc-security-ask",
    )

    assert result["success"] is False
    assert "security approval" in str(result["error"])
    assert tool_gateway.invoke_calls == 0


@pytest.mark.asyncio
async def test_tool_loop_uses_trusted_params_from_security_boundary() -> None:
    tool_gateway = _RecordingToolGateway()
    agent = _build_agent(boundary=_TrustRewriteBoundary(), tool_gateway=tool_gateway)

    result = await agent._run_tool_loop(  # noqa: SLF001
        ToolLoopRequest(capability_id="tool.echo", params={"raw": "no"}),
        tool_name="echo",
        tool_call_id="tc-security-trust",
    )

    assert result["success"] is True
    assert tool_gateway.invoke_calls == 1
    assert tool_gateway.last_params is not None
    assert tool_gateway.last_params.get("trusted") == "yes"


@pytest.mark.asyncio
async def test_plan_entry_denied_by_security_policy_stops_before_execute() -> None:
    model = _RecordingModel()
    agent = _build_agent(
        boundary=_PlanDenyBoundary(),
        model=model,
        planner=_Planner(),
        validator=_Validator(),
    )

    result = await agent("run guarded task")

    assert result.success is False
    assert any("execute plan denied by security policy" in str(err) for err in result.errors)
    assert model.calls == 0
