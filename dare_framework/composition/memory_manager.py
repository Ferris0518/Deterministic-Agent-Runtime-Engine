from __future__ import annotations

from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, ENTRYPOINT_MEMORY
from dare_framework.core.context.protocols import IMemory


class MemoryManager(BaseComponentManager[IMemory]):
    def __init__(self, entry_points_loader: EntryPointLoader | None = None) -> None:
        super().__init__(ENTRYPOINT_MEMORY, IMemory, entry_points_loader, config_section="memory")
