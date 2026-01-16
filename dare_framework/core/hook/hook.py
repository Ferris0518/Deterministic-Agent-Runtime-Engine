from __future__ import annotations

from typing import runtime_checkable, Protocol

from dare_framework.core.configurable_component import IConfigurableComponent
from dare_framework.core.event.event import Event


@runtime_checkable
class IHook(IConfigurableComponent, Protocol):
    """Lifecycle hooks for observing runtime events (Interface_Layer_Design_v1.1)."""

    async def on_event(self, event: Event) -> None:
        """Handle a runtime event for logging or metrics."""
        ...
