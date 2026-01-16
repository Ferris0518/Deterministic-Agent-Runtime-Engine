from __future__ import annotations

from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, \
    ENTRYPOINT_MODEL_ADAPTERS
from dare_framework.core.models.model_adapter import IModelAdapter


class ModelAdapterManager(BaseComponentManager[IModelAdapter]):
    def __init__(self, entry_points_loader: EntryPointLoader | None = None) -> None:
        super().__init__(ENTRYPOINT_MODEL_ADAPTERS, IModelAdapter, entry_points_loader, config_section="llm")
