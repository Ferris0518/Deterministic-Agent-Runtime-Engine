from __future__ import annotations

from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, ENTRYPOINT_HOOKS
from dare_framework.core.hook.hook import IHook


class HookManager(BaseComponentManager[IHook]):
    def __init__(self, entry_points_loader: EntryPointLoader | None = None) -> None:
        super().__init__(ENTRYPOINT_HOOKS, IHook, entry_points_loader, config_section="hooks")
