import pytest

from dare_framework.components.base_context_assembler import BasicContextAssembler
from dare_framework.components.checkpoint import FileCheckpoint
from dare_framework.components.event_log import LocalEventLog
from dare_framework.components.tools.noop import NoOpTool
from dare_framework.components.plan_generator import DeterministicPlanGenerator
from dare_framework.components.policy_engine import AllowAllPolicyEngine
from dare_framework.components.registries import SkillRegistry, ToolRegistry
from dare_framework.components.remediator import NoOpRemediator
from dare_framework.components.tool_runtime import ToolRuntime
from dare_framework.components.validators.simple import SimpleValidator
from dare_framework.core.plan.models import ProposedStep, Task
from dare_framework.core.dare_utils import generator_id
from dare_framework.core.models.runtime_state import RuntimeState
from dare_framework.core.runtime_engine import AgentRuntime


@pytest.mark.asyncio
async def test_runtime_transitions_to_stopped(tmp_path):
    plan_generator = DeterministicPlanGenerator(
        [[ProposedStep(step_id=generator_id("step"), tool_name="noop", tool_input={})]]
    )

    tool_registry = ToolRegistry()
    tool_registry.register_tool(NoOpTool())
    skill_registry = SkillRegistry()

    policy_engine = AllowAllPolicyEngine()
    validator = SimpleValidator()
    tool_runtime = ToolRuntime(
        toolkit=tool_registry,
        skill_registry=skill_registry,
        policy_engine=policy_engine,
        validator=validator,
    )

    runtime = AgentRuntime(
        tool_runtime=tool_runtime,
        plan_generator=plan_generator,
        model_adapter=None,
        validator=validator,
        policy_engine=policy_engine,
        remediator=NoOpRemediator(),
        context_assembler=BasicContextAssembler(),
        event_log=LocalEventLog(path=str(tmp_path / "events.jsonl")),
        checkpoint=FileCheckpoint(path=str(tmp_path / "checkpoints")),
    )

    task = Task(description="noop")
    await runtime.init(task)
    result = await runtime.run(task, None)

    assert result.success is True
    assert result.session_summary is not None
    assert result.session_summary.success is True
    assert result.milestone_results[0].summary is not None
    assert runtime.get_state() == RuntimeState.STOPPED
