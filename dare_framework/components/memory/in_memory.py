from __future__ import annotations

from dare_framework.core.context.models import MemoryItem
from dare_framework.core.context.protocols import IMemory
from ...core.component_type import ComponentType
from ..base_component import ConfigurableComponent


class InMemoryMemory(ConfigurableComponent, IMemory):
    component_type = ComponentType.MEMORY

    def __init__(self) -> None:
        self._items: dict[str, tuple[str, dict]] = {}

    async def store(self, key: str, value: str, metadata: dict | None = None) -> None:
        self._items[key] = (value, metadata or {})

    async def search(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        matches = []
        for key, (value, metadata) in self._items.items():
            if query in value:
                matches.append((key, value, metadata))
        results = matches[:top_k]

        return [MemoryItem(key=key, value=value, metadata=metadata) for key, value, metadata in results]

    async def get(self, key: str) -> str | None:
        item = self._items.get(key)
        return item[0] if item else None
