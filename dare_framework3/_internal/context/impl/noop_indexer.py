"""No-op indexer implementation."""

from __future__ import annotations

from dare_framework3._internal.context.components import IIndexer
from dare_framework3._internal.context.types import IndexStatus


class NoOpIndexer(IIndexer):
    """Indexer that reports readiness without doing work."""

    async def ensure_index(self, scope: str) -> IndexStatus:
        _ = scope
        return IndexStatus(ready=True, details={"indexer": "noop"})

    async def add(self, scope: str, items: list[dict[str, object]]) -> None:
        _ = (scope, items)
