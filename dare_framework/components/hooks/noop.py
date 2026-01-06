from __future__ import annotations

from ...core.runtime import IHook
from ...core.models.config import ComponentType
from ...core.models.event import Event
from ..base_component import ConfigurableComponent


class NoOpHook(ConfigurableComponent, IHook):
    component_type = ComponentType.HOOK

    async def on_event(self, event: Event) -> None:
        return None
