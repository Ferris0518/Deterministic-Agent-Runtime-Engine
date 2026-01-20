"""Context domain component interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from dare_framework3._internal.context.types import AssembledContext, IndexStatus, Prompt, RetrievedContext

if TYPE_CHECKING:
    from dare_framework3._internal.execution.types import Budget


class IContextStrategy(Protocol):
    """Strategy for building prompts from assembled context."""

    async def build_prompt(self, assembled: AssembledContext) -> Prompt:
        ...


@runtime_checkable
class IMemory(Protocol):
    """Memory interface for retrieval and persistence."""

    async def retrieve(
        self,
        query: str,
        *,
        budget: "Budget | None" = None,
    ) -> list[dict[str, Any]]:
        ...

    async def add(self, items: list[dict[str, Any]]) -> None:
        ...


@runtime_checkable
class IPromptStore(Protocol):
    """Prompt template storage interface."""

    async def get(self, prompt_id: str) -> str | None:
        ...

    async def set(self, prompt_id: str, content: str) -> None:
        ...


class IRetriever(Protocol):
    """Retrieval component for context engineering."""

    async def retrieve(
        self,
        query: str,
        *,
        budget: "Budget | None" = None,
    ) -> RetrievedContext:
        ...


class IIndexer(Protocol):
    """Indexing component for retrieval readiness."""

    async def ensure_index(self, scope: str) -> IndexStatus:
        ...

    async def add(self, scope: str, items: list[dict[str, Any]]) -> None:
        ...
