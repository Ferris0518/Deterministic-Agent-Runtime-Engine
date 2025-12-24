from __future__ import annotations

from dataclasses import dataclass, field

from dare_framework.components.layer2 import IMemory
from dare_framework.core.models import MemoryItem


@dataclass
class InMemoryMemory(IMemory):
    _items: dict[str, MemoryItem] = field(default_factory=dict)

    async def store(self, key: str, value: str, metadata: dict | None = None) -> None:
        self._items[key] = MemoryItem(key=key, value=value, metadata=metadata or {})

    async def search(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        if not query:
            return list(self._items.values())[:top_k]
        matches = [item for item in self._items.values() if query in item.value]
        return matches[:top_k]

    async def get(self, key: str) -> str | None:
        item = self._items.get(key)
        return item.value if item else None
