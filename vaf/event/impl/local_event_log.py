"""Local file-based event log implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from vaf.event.component import IEventLog
from vaf.event.types import Event


class LocalEventLog(IEventLog):
    """File-based event log that appends events to a JSONL file."""

    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def append(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> str:
        """Append an event to the log."""
        event = Event(event_type=event_type, payload=payload)
        
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "event_id": event.event_id,
                "event_type": event.event_type,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat(),
            }) + "\n")
        
        return event.event_id

    async def query(
        self,
        *,
        event_type: str | None = None,
        limit: int = 100,
    ) -> Sequence[Event]:
        """Query events from the log."""
        events: list[Event] = []
        
        if not self._path.exists():
            return events
        
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if event_type and data.get("event_type") != event_type:
                        continue
                    events.append(Event(
                        event_type=data["event_type"],
                        payload=data["payload"],
                        event_id=data["event_id"],
                    ))
                except json.JSONDecodeError:
                    continue
        
        return events[-limit:]
