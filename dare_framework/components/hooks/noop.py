from __future__ import annotations

from dare_framework.core.hook.hook import IHook
from ...core.component_type import ComponentType
from dare_framework.core.event.event import Event
from ..base_component import ConfigurableComponent


class NoOpHook(ConfigurableComponent, IHook):
    component_type = ComponentType.HOOK

    async def on_event(self, event: Event) -> None:
        return None
