from __future__ import annotations

import asyncio
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dare_framework import (
    AgentRuntime,
    AllowAllPolicy,
    BasicToolkit,
    DefaultContextAssembler,
    DefaultPlanGenerator,
    DefaultRemediator,
    DefaultToolRuntime,
    InMemoryCheckpoint,
    InMemoryEventLog,
)
from dare_framework.components.layer2 import IModelAdapter
from dare_framework.core.models import GenerateOptions, Message, ModelResponse, Task, ToolCall, ToolDefinition
from dare_framework.tools import NoopTool
from dare_framework.validators import DefaultValidator


class ScriptedModelAdapter(IModelAdapter):
    """Returns a single tool call, then declares done."""

    def __init__(self) -> None:
        self._step = 0

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        options: GenerateOptions | None = None,
    ) -> ModelResponse:
        if self._step == 0:
            self._step += 1
            return ModelResponse(
                content="calling noop",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="noop",
                        input={"message": "hello runtime"},
                    )
                ],
            )

        return ModelResponse(content="done", tool_calls=[])

    async def generate_structured(self, messages: list[Message], output_schema: type) -> object:
        return output_schema()


async def main() -> None:
    toolkit = BasicToolkit()
    toolkit.register_tool(NoopTool())

    runtime = AgentRuntime(
        event_log=InMemoryEventLog(),
        tool_runtime=DefaultToolRuntime(toolkit, AllowAllPolicy()),
        policy_engine=AllowAllPolicy(),
        plan_generator=DefaultPlanGenerator(),
        validator=DefaultValidator(toolkit=toolkit),
        remediator=DefaultRemediator(),
        context_assembler=DefaultContextAssembler(),
        model_adapter=ScriptedModelAdapter(),
        checkpoint=InMemoryCheckpoint(),
    )

    task = Task(description="Run the main flow with default components")
    await runtime.init(task)
    result = await runtime.run(task, deps=None)

    print("Success:", result.success)
    if result.session_summary:
        print("Milestones:", result.session_summary.milestone_count)
        print("Deliverables:", result.session_summary.key_deliverables)


if __name__ == "__main__":
    asyncio.run(main())
