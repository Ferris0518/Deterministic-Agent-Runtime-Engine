from __future__ import annotations

from typing import Protocol, Generic

from dare_framework.core.component import DepsT, OutputT
from dare_framework.core.plan.models import Task
from dare_framework.core.context.models import RunResult


class IAgent(Protocol, Generic[DepsT, OutputT]):
    """Composition-layer wrapper that drives a configured runtime (Interface_Layer_Design_v1.1)."""

    async def run(self, task: Task, deps: DepsT) -> RunResult[OutputT]:
        """Run the configured runtime with provided dependencies."""
        ...
