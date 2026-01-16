from __future__ import annotations

from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, \
    ENTRYPOINT_CONFIG_PROVIDERS
from dare_framework.core.config.config_provider import IConfigProvider


class ConfigProviderManager(BaseComponentManager[IConfigProvider]):
    def __init__(self, entry_points_loader: EntryPointLoader | None = None) -> None:
        super().__init__(ENTRYPOINT_CONFIG_PROVIDERS, IConfigProvider, entry_points_loader, config_section=None)
