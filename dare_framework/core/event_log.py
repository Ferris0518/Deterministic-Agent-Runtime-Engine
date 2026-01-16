from __future__ import annotations

from typing import Protocol

from dare_framework.core.event.event import Event, EventFilter


class IEventLog(Protocol):
    """Append-only event log for audit and WORM guarantees (Architecture_Final_Review_v1.3)."""

    async def append(self, event: Event) -> str:
        """Append an event and return its event identifier or hash."""
        ...

    async def query(self, filter: EventFilter | None = None, offset: int = 0, limit: int = 100) -> list[Event]:
        """Query a window of events for replay or inspection."""
        ...

    async def verify_chain(self) -> bool:
        """Verify hash-chain integrity for audit purposes."""
        ...

    async def get_checkpoint_events(self, checkpoint_id: str) -> list[Event]:
        """Return events associated with a checkpoint."""
        ...
