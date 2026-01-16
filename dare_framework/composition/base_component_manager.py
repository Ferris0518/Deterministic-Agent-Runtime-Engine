from __future__ import annotations

from importlib import metadata
from typing import Any, Callable, Generic, TypeVar

from dare_framework.core.component import IComponent
from dare_framework.core.component_register import IComponentRegistrar
from dare_framework.core.configurable_component import IConfigurableComponent
from dare_framework.core.models.prompt_store import IPromptStore
from dare_framework.core.config.config import Config

EntryPointLoader = Callable[[], Any]
TComponent = TypeVar("TComponent", bound=IComponent)

ENTRYPOINT_VALIDATORS = "dare_framework.validators"
ENTRYPOINT_MEMORY = "dare_framework.memory"
ENTRYPOINT_MODEL_ADAPTERS = "dare_framework.model_adapters"
ENTRYPOINT_TOOLS = "dare_framework.tools"
ENTRYPOINT_SKILLS = "dare_framework.skills"
ENTRYPOINT_MCP_CLIENTS = "dare_framework.mcp_clients"
ENTRYPOINT_HOOKS = "dare_framework.hooks"
ENTRYPOINT_CONFIG_PROVIDERS = "dare_framework.config_providers"
ENTRYPOINT_PROMPT_STORES = "dare_framework.prompt_stores"


class BaseComponentManager(IComponentRegistrar, Generic[TComponent]):
    def __init__(
        self,
        entrypoint_group: str,
        expected_type: type[TComponent],
        entry_points_loader: EntryPointLoader | None = None,
        config_section: str | None = None,
    ) -> None:
        self._entrypoint_group = entrypoint_group
        self._expected_type = expected_type
        self._entry_points_loader = entry_points_loader or metadata.entry_points
        self._components: list[TComponent] = []
        self._registered_ids: set[int] = set()
        self._config_section = config_section

    async def load(
        self,
        config: Config | None,
        prompt_store: IPromptStore | None = None,
    ) -> list[TComponent]:
        discovered = self._discover_components()
        ordered = sorted(discovered, key=lambda comp: getattr(comp, "order", 100))
        for component in ordered:
            if not self._is_enabled(component, config):
                continue
            await component.init(config, prompt_store)
            component.register(self)
        return list(self._components)

    def _is_enabled(self, component: TComponent, config: Config | None) -> bool:
        if config is None or not isinstance(component, IConfigurableComponent):
            return True
        return config.is_component_enabled(component.component_type, component.component_name)

    def register_component(self, component: IComponent) -> None:
        if not isinstance(component, self._expected_type):
            return
        component_id = id(component)
        if component_id in self._registered_ids:
            return
        self._registered_ids.add(component_id)
        typed_component = component
        self._components.append(typed_component)
        self._register_component(typed_component)

    def _register_component(self, component: TComponent) -> None:
        return None

    def _discover_components(self) -> list[TComponent]:
        entry_points = self._entry_points_loader()
        if hasattr(entry_points, "select"):
            group_entries = list(entry_points.select(group=self._entrypoint_group))
        else:
            group_entries = list(entry_points.get(self._entrypoint_group, []))

        components: list[TComponent] = []
        for entry_point in group_entries:
            component = self._load_entry_point(entry_point)
            if component is not None:
                components.append(component)
        return components

    def _load_entry_point(self, entry_point) -> TComponent | None:
        loaded = entry_point.load()
        if isinstance(loaded, type):
            instance = loaded()
        elif callable(loaded):
            instance = loaded()
        else:
            return None
        if not isinstance(instance, self._expected_type):
            return None
        return instance

