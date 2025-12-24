from __future__ import annotations

from ..core.interfaces import IMemory


class InMemoryMemory(IMemory):
    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, text: str, metadata: dict | None = None) -> None:
        self._items.append(text)

    def search(self, query: str, limit: int = 5) -> list[str]:
        if not query:
            return self._items[:limit]
        return [item for item in self._items if query in item][:limit]
