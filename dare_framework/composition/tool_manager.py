from __future__ import annotations

from dare_framework.components.registries import ToolRegistry
from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, ENTRYPOINT_TOOLS
from dare_framework.core.models.prompt_store import IPromptStore
from dare_framework.core.config.config import Config
from dare_framework.core.tool.protocols import ITool


class ToolManager(BaseComponentManager[ITool]):
    def __init__(
        self,
        tool_registry: ToolRegistry,
        entry_points_loader: EntryPointLoader | None = None,
    ) -> None:
        super().__init__(ENTRYPOINT_TOOLS, ITool, entry_points_loader, config_section="tools")
        self._tool_registry = tool_registry

    def _register_component(self, component: ITool) -> None:
        self._tool_registry.register_tool(component)

    async def load(
        self,
        config: Config | None,
        prompt_store: IPromptStore | None = None,
    ) -> list[ITool]:
        return await super().load(config, prompt_store)
