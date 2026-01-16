from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class Event:
    event_type: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    prev_hash: str | None = None
    event_hash: str | None = None


@dataclass(frozen=True)
class EventFilter:
    event_type: str | None = None
    milestone_id: str | None = None
    checkpoint_id: str | None = None
    run_id: str | None = None
