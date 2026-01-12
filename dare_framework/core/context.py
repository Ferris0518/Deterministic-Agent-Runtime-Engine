from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .models.context import AssembledContext
from .models.plan import Milestone
from .models.context import MilestoneContext
from .models.runtime import RunContext
from .composition import IConfigurableComponent


class IContextAssembler(Protocol):
    """Assembles and compresses runtime context (Architecture_Final_Review_v1.3)."""

    async def assemble(
        self,
        milestone: Milestone,
        milestone_ctx: MilestoneContext,
        ctx: RunContext,
    ) -> AssembledContext:
        """Build an assembled context for the milestone."""
        ...

    async def compress(self, context: AssembledContext, max_tokens: int) -> AssembledContext:
        """Compress assembled context to meet token limits."""
        ...


@runtime_checkable
class IModelAdapter(IConfigurableComponent, Protocol):
    """Model adapter for LLM inference (Interface_Layer_Design_v1.1)."""

    async def generate(
        self,
        messages: list["Message"],
        tools: list["ToolDefinition"] | None = None,
        options: "GenerateOptions" | None = None,
    ) -> "ModelResponse":
        """Generate a response from model messages and optional tools."""
        ...

    async def generate_structured(self, messages: list["Message"], output_schema: type[Any]) -> Any:
        """Generate structured output using a schema."""
        ...


@runtime_checkable
class IMemory(IConfigurableComponent, Protocol):
    """Memory storage and retrieval (Interface_Layer_Design_v1.1)."""

    async def store(self, key: str, value: str, metadata: dict | None = None) -> None:
        """Persist a memory entry."""
        ...

    async def search(self, query: str, top_k: int = 5) -> list["MemoryItem"]:
        """Search for relevant memories by query."""
        ...

    async def get(self, key: str) -> str | None:
        """Retrieve a stored memory by key."""
        ...


from .models.context import GenerateOptions, Message, ModelResponse
from .models.memory import MemoryItem
from .models.tool import ToolDefinition
