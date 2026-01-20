"""No-op retriever implementation."""

from __future__ import annotations

from dare_framework3._internal.context.components import IRetriever
from dare_framework3._internal.context.types import RetrievedContext
from dare_framework3._internal.execution.types import Budget


class NoOpRetriever(IRetriever):
    """Retriever that always returns an empty context."""

    async def retrieve(
        self,
        query: str,
        *,
        budget: Budget | None = None,
    ) -> RetrievedContext:
        _ = (query, budget)
        return RetrievedContext(items=[])
