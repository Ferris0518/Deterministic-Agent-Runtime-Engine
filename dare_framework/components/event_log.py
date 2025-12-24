from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable
import json

from dare_framework.components.interfaces import IEventLog
from dare_framework.core.events import Event, EventFilter


@dataclass
class InMemoryEventLog(IEventLog):
    def __init__(self) -> None:
        self._events: list[Event] = []

    async def append(self, event: Event) -> str:
        event_id = f"event_{len(self._events) + 1}"
        self._events.append(event)
        return event_id

    async def query(
        self,
        filter: EventFilter | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Event]:
        events: Iterable[Event] = self._events

        if filter:
            if filter.event_types:
                event_types = set(filter.event_types)
                events = [event for event in events if event.event_type in event_types]

            if filter.milestone_id:
                events = [
                    event
                    for event in events
                    if event.payload.get("milestone_id") == filter.milestone_id
                ]

            if filter.since_timestamp is not None:
                events = [
                    event
                    for event in events
                    if event.timestamp >= filter.since_timestamp
                ]

            if filter.until_timestamp is not None:
                events = [
                    event
                    for event in events
                    if event.timestamp <= filter.until_timestamp
                ]

        sliced = list(events)[offset : offset + limit]
        return sliced

    async def verify_chain(self) -> bool:
        return True

    async def get_checkpoint_events(self, checkpoint_id: str) -> list[Event]:
        return [
            event
            for event in self._events
            if event.payload.get("checkpoint_id") == checkpoint_id
        ]


class FileEventLog(IEventLog):
    def __init__(self, path: str = ".dare/event_log.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[dict[str, object]] = []
        if self._path.exists():
            self._load_existing()

    async def append(self, event: Event) -> str:
        event_id = f"event_{len(self._records) + 1}"
        prev_hash = self._records[-1]["event_hash"] if self._records else None
        event_hash = self._hash_event(event, prev_hash)
        record = {
            "event_id": event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "payload": event.payload,
            "prev_hash": prev_hash,
            "event_hash": event_hash,
        }
        self._records.append(record)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return event_id

    async def query(
        self,
        filter: EventFilter | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Event]:
        events: Iterable[Event] = [self._to_event(record) for record in self._records]

        if filter:
            if filter.event_types:
                event_types = set(filter.event_types)
                events = [event for event in events if event.event_type in event_types]

            if filter.milestone_id:
                events = [
                    event
                    for event in events
                    if event.payload.get("milestone_id") == filter.milestone_id
                ]

            if filter.since_timestamp is not None:
                events = [
                    event
                    for event in events
                    if event.timestamp >= filter.since_timestamp
                ]

            if filter.until_timestamp is not None:
                events = [
                    event
                    for event in events
                    if event.timestamp <= filter.until_timestamp
                ]

        return list(events)[offset : offset + limit]

    async def verify_chain(self) -> bool:
        prev_hash = None
        for record in self._records:
            event = self._to_event(record)
            if record.get("prev_hash") != prev_hash:
                return False
            expected_hash = self._hash_event(event, prev_hash)
            if record.get("event_hash") != expected_hash:
                return False
            prev_hash = record.get("event_hash")
        return True

    async def get_checkpoint_events(self, checkpoint_id: str) -> list[Event]:
        return [
            self._to_event(record)
            for record in self._records
            if record.get("payload", {}).get("checkpoint_id") == checkpoint_id
        ]

    def _hash_event(self, event: Event, prev_hash: str | None) -> str:
        payload = json.dumps(
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "payload": event.payload,
                "prev_hash": prev_hash,
            },
            sort_keys=True,
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def _to_event(self, record: dict[str, object]) -> Event:
        return Event(
            event_type=str(record.get("event_type", "")),
            timestamp=float(record.get("timestamp", 0.0)),
            payload=record.get("payload", {}) or {},
        )

    def _load_existing(self) -> None:
        with self._path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if isinstance(record, dict):
                    self._records.append(record)
