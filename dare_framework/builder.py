from __future__ import annotations

from typing import Generic, Iterable, TypeVar

from dare_framework.components.checkpoint import InMemoryCheckpoint
from dare_framework.components.context_assembler import DefaultContextAssembler
from dare_framework.components.event_log import InMemoryEventLog
from dare_framework.components.mcp_toolkit import MCPToolkit
from dare_framework.components.plan_generator import DefaultPlanGenerator
from dare_framework.components.policy_engine import AllowAllPolicy
from dare_framework.components.registries import SkillRegistry
from dare_framework.components.remediator import DefaultRemediator
from dare_framework.components.tool_runtime import DefaultToolRuntime
from dare_framework.components.toolkit import BasicToolkit
from dare_framework.core.models import RunResult, Task
from dare_framework.core.runtime import AgentRuntime, IRuntime
from dare_framework.models import NoopModelAdapter
from dare_framework.tools import NoopTool
from dare_framework.validators import DefaultValidator
from dare_framework.components.interfaces import (
    ICheckpoint,
    IContextAssembler,
    IEventLog,
    IHook,
    IMCPClient,
    IModelAdapter,
    IPlanGenerator,
    IPolicyEngine,
    IRemediator,
    IValidator,
)
from dare_framework.components.interfaces import ITool, ISkill
from dare_framework.memory import InMemoryMemory

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


class Agent(Generic[DepsT, OutputT]):
    def __init__(self, runtime: IRuntime[DepsT, OutputT]) -> None:
        self._runtime = runtime

    async def run(self, task: Task, deps: DepsT) -> RunResult[OutputT]:
        await self._runtime.init(task)
        return await self._runtime.run(task, deps)


class AgentBuilder(Generic[DepsT, OutputT]):
    def __init__(self, name: str) -> None:
        self._name = name
        self._toolkit = BasicToolkit()
        self._skill_registry = SkillRegistry()
        self._model_adapter: IModelAdapter | None = None
        self._memory = InMemoryMemory()
        self._hooks: list[IHook] = []
        self._plan_generator: IPlanGenerator | None = None
        self._validator: IValidator | None = None
        self._policy_engine: IPolicyEngine | None = None
        self._remediator: IRemediator | None = None
        self._context_assembler: IContextAssembler | None = None
        self._event_log: IEventLog | None = None
        self._checkpoint: ICheckpoint | None = None
        self._runtime: IRuntime | None = None
        self._mcp_clients: list[IMCPClient] = []

    @classmethod
    def quick_start(cls, name: str) -> "AgentBuilder":
        builder = cls(name)
        builder.with_tools(NoopTool())
        builder.with_model(NoopModelAdapter())
        builder.with_plan_generator(DefaultPlanGenerator())
        return builder

    def description(self, text: str) -> "AgentBuilder":
        self._name = text
        return self

    def with_tools(self, *tools: ITool) -> "AgentBuilder":
        self._toolkit.register_many(tools)
        return self

    def with_skills(self, *skills: ISkill) -> "AgentBuilder":
        self._skill_registry.register_many(skills)
        return self

    def with_model(self, model: IModelAdapter) -> "AgentBuilder":
        self._model_adapter = model
        return self

    def with_memory(self, memory: InMemoryMemory) -> "AgentBuilder":
        self._memory = memory
        return self

    def with_hook(self, hook: IHook) -> "AgentBuilder":
        self._hooks.append(hook)
        return self

    def with_runtime(self, runtime: IRuntime) -> "AgentBuilder":
        self._runtime = runtime
        return self

    def with_plan_generator(self, plan_generator: IPlanGenerator) -> "AgentBuilder":
        self._plan_generator = plan_generator
        return self

    def with_validator(self, validator: IValidator) -> "AgentBuilder":
        self._validator = validator
        return self

    def with_policy_engine(self, policy_engine: IPolicyEngine) -> "AgentBuilder":
        self._policy_engine = policy_engine
        return self

    def with_remediator(self, remediator: IRemediator) -> "AgentBuilder":
        self._remediator = remediator
        return self

    def with_context_assembler(self, context_assembler: IContextAssembler) -> "AgentBuilder":
        self._context_assembler = context_assembler
        return self

    def with_event_log(self, event_log: IEventLog) -> "AgentBuilder":
        self._event_log = event_log
        return self

    def with_checkpoint(self, checkpoint: ICheckpoint) -> "AgentBuilder":
        self._checkpoint = checkpoint
        return self

    def with_mcp(self, *clients: IMCPClient) -> "AgentBuilder":
        self._mcp_clients.extend(clients)
        return self

    def build(self) -> Agent[DepsT, OutputT]:
        if self._mcp_clients:
            raise RuntimeError("MCP clients require build_async() for initialization")
        return self._build()

    async def build_async(self) -> Agent[DepsT, OutputT]:
        if self._runtime is not None:
            return Agent(self._runtime)
        if self._mcp_clients:
            mcp_toolkit = MCPToolkit(self._mcp_clients)
            await mcp_toolkit.initialize()
            self._toolkit.register_many(mcp_toolkit.export_tools())
        return self._build()

    def _build(self) -> Agent[DepsT, OutputT]:
        if self._runtime is not None:
            return Agent(self._runtime)

        if self._toolkit.get_tool("noop") is None:
            self._toolkit.register_tool(NoopTool())

        plan_generator = self._plan_generator or DefaultPlanGenerator()
        validator = self._validator or DefaultValidator(toolkit=self._toolkit)
        policy_engine = self._policy_engine or AllowAllPolicy()
        remediator = self._remediator or DefaultRemediator()
        context_assembler = self._context_assembler or DefaultContextAssembler()
        event_log = self._event_log or InMemoryEventLog()
        checkpoint = self._checkpoint or InMemoryCheckpoint()
        model_adapter = self._model_adapter or NoopModelAdapter()

        tool_runtime = DefaultToolRuntime(
            self._toolkit,
            policy_engine,
            skill_registry=self._skill_registry,
            validator=validator,
        )

        runtime = AgentRuntime(
            event_log=event_log,
            tool_runtime=tool_runtime,
            policy_engine=policy_engine,
            plan_generator=plan_generator,
            validator=validator,
            remediator=remediator,
            context_assembler=context_assembler,
            model_adapter=model_adapter,
            checkpoint=checkpoint,
            hooks=self._hooks,
        )
        return Agent(runtime)
