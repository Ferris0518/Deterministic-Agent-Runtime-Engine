from __future__ import annotations

from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, \
    ENTRYPOINT_PROMPT_STORES
from dare_framework.core.models.prompt_store import IPromptStore


class PromptStoreManager(BaseComponentManager[IPromptStore]):
    def __init__(self, entry_points_loader: EntryPointLoader | None = None) -> None:
        super().__init__(ENTRYPOINT_PROMPT_STORES, IPromptStore, entry_points_loader, config_section="prompt_store")
