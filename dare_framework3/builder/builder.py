"""AgentBuilder - fluent builder for composing agents."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dare_framework3.builder.agent import Agent
from dare_framework3.presets.base import Preset
from dare_framework3._internal.execution.types import Budget
from dare_framework3._internal.execution.kernel import IRunLoop
from dare_framework3._internal.execution.impl.noop_run_loop import NoOpRunLoop

if TYPE_CHECKING:
    from dare_framework3.interfaces import (
        IHook,
        IModelAdapter,
        IMemory,
        IPlanner,
        IRemediator,
        IValidator,
        ITool,
    )


class AgentBuilder:
    """Layer 3 builder for composing the Kernel and pluggable components."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._run_loop: IRunLoop | None = None
        self._model_adapter: "IModelAdapter | None" = None
        self._planner: "IPlanner | None" = None
        self._validator: "IValidator | None" = None
        self._remediator: "IRemediator | None" = None
        self._memory: "IMemory | None" = None
        self._tools: list["ITool"] = []
        self._hooks: list["IHook"] = []
        self._budget = Budget()

    def with_run_loop(self, run_loop: IRunLoop) -> "AgentBuilder":
        self._run_loop = run_loop
        return self

    def with_model(self, model: "IModelAdapter") -> "AgentBuilder":
        self._model_adapter = model
        return self

    def with_planner(self, planner: "IPlanner") -> "AgentBuilder":
        self._planner = planner
        return self

    def with_validator(self, validator: "IValidator") -> "AgentBuilder":
        self._validator = validator
        return self

    def with_remediator(self, remediator: "IRemediator") -> "AgentBuilder":
        self._remediator = remediator
        return self

    def with_memory(self, memory: "IMemory") -> "AgentBuilder":
        self._memory = memory
        return self

    def with_tools(self, *tools: "ITool") -> "AgentBuilder":
        self._tools.extend(tools)
        return self

    def with_hooks(self, *hooks: "IHook") -> "AgentBuilder":
        self._hooks.extend(hooks)
        return self

    def with_budget(self, budget: Budget) -> "AgentBuilder":
        self._budget = budget
        return self

    def with_preset(self, preset: Preset) -> "AgentBuilder":
        return preset.configure(self)

    def build(self) -> Agent:
        run_loop = self._run_loop or NoOpRunLoop()
        return Agent(name=self._name, run_loop=run_loop)
