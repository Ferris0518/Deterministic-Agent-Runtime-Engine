import pytest

from agent_framework.checkpoint import FileCheckpoint
from agent_framework.defaults import DeterministicPlanGenerator, NoOpTool
from agent_framework.event_log import LocalEventLog
from agent_framework.models import PlanStep, RuntimeState, Task
from agent_framework.registries import SkillRegistry, ToolRegistry
from agent_framework.runtime import AgentRuntime
from agent_framework.tool_runtime import ToolRuntime
from agent_framework.defaults import AllowAllPolicyEngine, SimpleValidator


@pytest.mark.asyncio
async def test_runtime_transitions_to_stopped(tmp_path):
    plan_generator = DeterministicPlanGenerator(
        [[PlanStep(tool_name="noop", tool_input={})]]
    )

    tool_registry = ToolRegistry()
    tool_registry.register_tool(NoOpTool())
    skill_registry = SkillRegistry()

    tool_runtime = ToolRuntime(
        toolkit=tool_registry,
        skill_registry=skill_registry,
        policy_engine=AllowAllPolicyEngine(),
        validator=SimpleValidator(),
    )

    runtime = AgentRuntime(
        tool_runtime=tool_runtime,
        plan_generator=plan_generator,
        event_log=LocalEventLog(path=str(tmp_path / "events.jsonl")),
        checkpoint=FileCheckpoint(path=str(tmp_path / "checkpoints")),
    )

    task = Task(description="noop")
    await runtime.init(task)
    result = await runtime.run(task, None)

    assert result.success is True
    assert runtime.get_state() == RuntimeState.STOPPED
