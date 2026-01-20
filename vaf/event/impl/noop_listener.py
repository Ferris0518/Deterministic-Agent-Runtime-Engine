"""No-op event listener implementation."""

from __future__ import annotations

from vaf.event.component import IEventListener
from vaf.event.types import Event


class NoopListener(IEventListener):
    """Event listener that does nothing."""

    async def on_event(self, event: Event) -> None:
        """Handle an event (no-op)."""
        pass
