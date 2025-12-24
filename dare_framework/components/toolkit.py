from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from dare_framework.components.interfaces import ITool, IToolkit


@dataclass
class BasicToolkit(IToolkit):
    _tools: dict[str, ITool] = field(default_factory=dict)

    def register_tool(self, tool: ITool) -> None:
        self._tools[tool.name] = tool

    def register_many(self, tools: Iterable[ITool]) -> None:
        for tool in tools:
            self.register_tool(tool)

    def get_tool(self, name: str) -> ITool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ITool]:
        return list(self._tools.values())

    def activate_group(self, group_name: str) -> None:
        return None
