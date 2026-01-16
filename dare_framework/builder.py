from __future__ import annotations

from typing import Generic, TypeVar

from dare_framework.components.base_context_assembler import BasicContextAssembler
from dare_framework.components.checkpoint import FileCheckpoint
from dare_framework.components.event_log import LocalEventLog
from dare_framework.components.hooks.noop import NoOpHook
from dare_framework.components.memory.in_memory import InMemoryMemory
from dare_framework.components.model_adapters.mock import MockModelAdapter
from dare_framework.components.mcp_toolkit import MCPToolkit
from dare_framework.components.tools.noop import NoOpTool
from dare_framework.components.plan_generator import DeterministicPlanGenerator
from dare_framework.components.policy_engine import AllowAllPolicyEngine
from dare_framework.components.prompt_stores.in_memory import InMemoryPromptStore
from dare_framework.components.registries import SkillRegistry, ToolRegistry
from dare_framework.components.remediator import NoOpRemediator
from dare_framework.components.tool_runtime import ToolRuntime
from dare_framework.components.validators.composite import CompositeValidator
from dare_framework.components.validators.simple import SimpleValidator
from dare_framework.components.config_providers.default_config_provider import DefaultConfigProvider
from dare_framework.composition.validator_manager import ValidatorManager
from dare_framework.composition.memory_manager import MemoryManager
from dare_framework.composition.model_adapter_manager import ModelAdapterManager
from dare_framework.composition.prompt_store_manager import PromptStoreManager
from dare_framework.composition.config_provider_manager import ConfigProviderManager
from dare_framework.composition.hook_manager import HookManager
from dare_framework.composition.mcp_client_manager import MCPClientManager
from dare_framework.composition.skill_manager import SkillManager
from dare_framework.composition.tool_manager import ToolManager
from dare_framework.core.agent import IAgent
from dare_framework.core.config.config_provider import IConfigProvider
from dare_framework.core.models.prompt_store import IPromptStore
from dare_framework.core.context.protocols import ICheckpoint, IContextAssembler, IPolicyEngine
from dare_framework.core.context.models import RunResult
from dare_framework.core.models.model_adapter import IModelAdapter
from dare_framework.core.plan.plan_generator import IPlanGenerator
from dare_framework.core.remediator.remediator import IRemediator
from dare_framework.core.runtime import IRuntime
from dare_framework.core.event_log import IEventLog
from dare_framework.core.validator.validator import IValidator
from dare_framework.core.config.config import Config
from dare_framework.core.plan.models import ProposedStep, Task
from dare_framework.core.dare_utils import generator_id
from dare_framework.core.runtime_engine import AgentRuntime

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


class Agent(IAgent[DepsT, OutputT]):
    def __init__(self, runtime: IRuntime[DepsT, OutputT]) -> None:
        self._runtime = runtime

    async def run(self, task: Task, deps: DepsT) -> RunResult[OutputT]:
        await self._runtime.init(task)
        return await self._runtime.run(task, deps)


class AgentBuilder(Generic[DepsT, OutputT]):
    def __init__(self, name: str) -> None:
        self._name = name
        self._tool_registry = ToolRegistry()
        self._skill_registry = SkillRegistry()
        self._model_adapter: IModelAdapter | None = None
        self._memory = InMemoryMemory()
        self._memory_set = False
        self._config_provider: IConfigProvider | None = None
        self._config_provider_set = False
        self._prompt_store: IPromptStore | None = None
        self._prompt_store_set = False
        self._config = Config()
        self._hooks = [NoOpHook()]
        self._plan_generator: IPlanGenerator | None = None
        self._validator: IValidator | None = None
        self._policy_engine: IPolicyEngine | None = None
        self._remediator: IRemediator | None = None
        self._context_assembler: IContextAssembler | None = None
        self._event_log: IEventLog | None = None
        self._checkpoint: ICheckpoint | None = None
        self._runtime: IRuntime | None = None
        self._mcp_clients = []

    @classmethod
    def quick_start(cls, name: str, model: str | None = None) -> "AgentBuilder":
        builder = cls(name)
        builder._model_adapter = MockModelAdapter([model or "ok"])
        builder.with_tools(NoOpTool())
        builder._plan_generator = DeterministicPlanGenerator(
            [[ProposedStep(step_id=generator_id("step"), tool_name="noop", tool_input={})]]
        )
        return builder

    def description(self, text: str) -> "AgentBuilder":
        self._name = text
        return self

    def with_tools(self, *tools) -> "AgentBuilder":
        self._tool_registry.register_many(tools)
        return self

    def with_skills(self, *skills) -> "AgentBuilder":
        self._skill_registry.register_many(skills)
        return self

    def with_model(self, model: IModelAdapter) -> "AgentBuilder":
        self._model_adapter = model
        return self

    def with_memory(self, memory) -> "AgentBuilder":
        self._memory = memory
        self._memory_set = True
        return self

    def with_config_provider(self, provider: IConfigProvider) -> "AgentBuilder":
        self._config_provider = provider
        self._config_provider_set = True
        return self

    def with_prompt_store(self, store: IPromptStore) -> "AgentBuilder":
        self._prompt_store = store
        self._prompt_store_set = True
        return self

    def with_hook(self, hook) -> "AgentBuilder":
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

    def with_mcp(self, *clients) -> "AgentBuilder":
        self._mcp_clients.extend(clients)
        return self

    def build(self) -> Agent[DepsT, OutputT]:
        if self._mcp_clients:
            raise RuntimeError("MCP clients require build_async() for initialization")
        return self._build()

    async def build_async(self) -> Agent[DepsT, OutputT]:
        if self._runtime is not None:
            return Agent(self._runtime)
        await self._load_components()
        if self._mcp_clients:
            mcp_toolkit = MCPToolkit(self._mcp_clients)
            await mcp_toolkit.initialize()
            for tool in mcp_toolkit.export_tools():
                self._tool_registry.register_tool(tool)
        return self._build()

    async def _load_components(self) -> None:
        config_manager = ConfigProviderManager()
        config_providers = await config_manager.load(None)
        config_provider = self._select_config_provider(config_providers)
        self._config = config_provider.current()

        prompt_manager = PromptStoreManager()
        prompt_stores = await prompt_manager.load(self._config)
        prompt_store = self._select_prompt_store(prompt_stores)

        validator_manager = ValidatorManager()
        validators = await validator_manager.load(self._config, prompt_store)
        if self._validator is None and validators:
            self._validator = CompositeValidator(validators)

        model_adapter_manager = ModelAdapterManager()
        model_adapters = await model_adapter_manager.load(self._config, prompt_store)
        if self._model_adapter is None and model_adapters:
            self._model_adapter = model_adapters[0]

        memory_manager = MemoryManager()
        memories = await memory_manager.load(self._config, prompt_store)
        if not self._memory_set and memories:
            self._memory = memories[0]

        mcp_manager = MCPClientManager()
        mcp_clients = await mcp_manager.load(self._config, prompt_store)
        if not self._mcp_clients and mcp_clients:
            self._mcp_clients = list(mcp_clients)

        hook_manager = HookManager()
        hooks = await hook_manager.load(self._config, prompt_store)
        self._hooks.extend(hooks)

        tool_manager = ToolManager(self._tool_registry)
        await tool_manager.load(self._config, prompt_store)

        skill_manager = SkillManager(self._skill_registry)
        await skill_manager.load(self._config, prompt_store)

    def _select_config_provider(self, discovered: list[IConfigProvider]) -> IConfigProvider:
        if self._config_provider_set and self._config_provider is not None:
            return self._config_provider
        if discovered:
            self._config_provider = discovered[0]
            return discovered[0]
        fallback = DefaultConfigProvider()
        self._config_provider = fallback
        return fallback

    def _select_prompt_store(self, discovered: list[IPromptStore]) -> IPromptStore | None:
        if self._prompt_store_set:
            return self._prompt_store
        if discovered:
            self._prompt_store = discovered[0]
            return discovered[0]
        fallback = InMemoryPromptStore()
        self._prompt_store = fallback
        return fallback

    def _build(self) -> Agent[DepsT, OutputT]:
        if self._runtime is not None:
            return Agent(self._runtime)
        validator = self._validator or CompositeValidator([SimpleValidator()])
        policy_engine = self._policy_engine or AllowAllPolicyEngine()
        remediator = self._remediator or NoOpRemediator()
        if self._prompt_store is None:
            self._prompt_store = InMemoryPromptStore()
        context_assembler = self._context_assembler or BasicContextAssembler(self._prompt_store)
        if self._plan_generator is None:
            if self._tool_registry.get_tool("noop") is None:
                self._tool_registry.register_tool(NoOpTool())
            plan_generator = DeterministicPlanGenerator(
                [[ProposedStep(step_id=generator_id("step"), tool_name="noop", tool_input={})]]
            )
        else:
            plan_generator = self._plan_generator

        tool_runtime = ToolRuntime(
            toolkit=self._tool_registry,
            skill_registry=self._skill_registry,
            policy_engine=policy_engine,
            validator=validator,
        )
        event_log = self._event_log or LocalEventLog()
        checkpoint = self._checkpoint or FileCheckpoint()
        runtime = AgentRuntime(
            tool_runtime=tool_runtime,
            plan_generator=plan_generator,
            model_adapter=self._model_adapter,
            validator=validator,
            policy_engine=policy_engine,
            remediator=remediator,
            context_assembler=context_assembler,
            event_log=event_log,
            checkpoint=checkpoint,
            hooks=self._hooks,
            config=self._config,
        )
        return Agent(runtime)
