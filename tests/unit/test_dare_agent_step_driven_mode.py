from __future__ import annotations

from typing import Any

import pytest

from dare_framework.agent import BaseAgent, DareAgent
from dare_framework.config import Config
from dare_framework.context import Context
from dare_framework.model.types import ModelInput, ModelResponse
from dare_framework.plan.types import StepResult, ValidatedPlan, ValidatedStep
from dare_framework.security.types import RiskLevel
from dare_framework.tool.types import ToolResult


class _RecordingModel:
    name = "recording-model"

    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, model_input: ModelInput, *, options: Any = None) -> ModelResponse:
        _ = (model_input, options)
        self.calls += 1
        return ModelResponse(content="model-path", tool_calls=[])


class _ToolGateway:
    def list_capabilities(self) -> list[Any]:
        return []

    async def invoke(self, capability_id: str, *, envelope: Any, **params: Any) -> ToolResult[dict[str, Any]]:
        _ = (capability_id, envelope, params)
        return ToolResult(success=True, output={"ok": True})


class _RecordingStepExecutor:
    def __init__(self) -> None:
        self.step_ids: list[str] = []

    async def execute_step(
        self,
        step: ValidatedStep,
        ctx: Any,
        previous_results: list[StepResult],
    ) -> StepResult:
        _ = (ctx, previous_results)
        self.step_ids.append(step.step_id)
        return StepResult(
            step_id=step.step_id,
            success=True,
            output={"step": step.step_id},
        )


def _build_agent(
    *,
    model: _RecordingModel,
    step_executor: _RecordingStepExecutor | None = None,
    execution_mode: str = "model_driven",
) -> DareAgent:
    return DareAgent(
        name="step-mode-agent",
        model=model,
        context=Context(config=Config()),
        tool_gateway=_ToolGateway(),
        step_executor=step_executor,
        execution_mode=execution_mode,
    )


@pytest.mark.asyncio
async def test_step_driven_execute_loop_runs_validated_steps_in_order() -> None:
    model = _RecordingModel()
    step_executor = _RecordingStepExecutor()
    agent = _build_agent(
        model=model,
        step_executor=step_executor,
        execution_mode="step_driven",
    )

    validated_plan = ValidatedPlan(
        success=True,
        plan_description="step plan",
        steps=[
            ValidatedStep(step_id="s1", capability_id="tool.one", risk_level=RiskLevel.READ_ONLY),
            ValidatedStep(step_id="s2", capability_id="tool.two", risk_level=RiskLevel.READ_ONLY),
        ],
    )

    result = await agent._run_execute_loop(validated_plan)  # noqa: SLF001 - runtime unit boundary test

    assert result["success"] is True
    assert step_executor.step_ids == ["s1", "s2"]
    assert result["outputs"] == [{"step": "s1"}, {"step": "s2"}]
    assert model.calls == 0


@pytest.mark.asyncio
async def test_step_driven_execute_loop_fails_without_validated_plan() -> None:
    model = _RecordingModel()
    step_executor = _RecordingStepExecutor()
    agent = _build_agent(
        model=model,
        step_executor=step_executor,
        execution_mode="step_driven",
    )

    result = await agent._run_execute_loop(None)  # noqa: SLF001 - runtime unit boundary test

    assert result["success"] is False
    assert any("validated plan" in error for error in result.get("errors", []))
    assert model.calls == 0


@pytest.mark.asyncio
async def test_default_execution_mode_remains_model_driven() -> None:
    model = _RecordingModel()
    agent = _build_agent(model=model)

    result = await agent._run_execute_loop(None)  # noqa: SLF001 - runtime unit boundary test

    assert result["success"] is True
    assert model.calls == 1


@pytest.mark.asyncio
async def test_builder_wires_execution_mode_and_step_executor() -> None:
    model = _RecordingModel()
    step_executor = _RecordingStepExecutor()

    agent = (
        BaseAgent.dare_agent_builder("builder-step-mode")
        .with_model(model)
        .with_execution_mode("step_driven")
        .with_step_executor(step_executor)
        .build()
    )
    agent = await agent

    assert getattr(agent, "_execution_mode") == "step_driven"
    assert getattr(agent, "_step_executor") is step_executor
