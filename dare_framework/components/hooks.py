from __future__ import annotations

from ..core.interfaces import IHook
from ..core.models import ComponentType, Event
from .base_component import ConfigurableComponent


class NoOpHook(ConfigurableComponent, IHook):
    component_type = ComponentType.HOOK
    async def on_event(self, event: Event) -> None:
        return None
