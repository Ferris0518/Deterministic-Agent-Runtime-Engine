"""Event domain data types.

VAF version - includes hook types (merged from hook/).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4


# =============================================================================
# Event
# =============================================================================

@dataclass(frozen=True)
class Event:
    """Append-only event record for audit and replay.
    
    Attributes:
        event_type: Type of event (e.g., "agent.reply", "tool.call")
        payload: Event data
        event_id: Unique event identifier
        timestamp: Event timestamp
    """
    event_type: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Hook Types (merged from hook/)
# =============================================================================

HookType = Literal[
    "agent.pre_reply",
    "agent.post_reply", 
    "tool.pre_call",
    "tool.post_call",
    "model.pre_generate",
    "model.post_generate",
]
"""Supported hook types for event-driven callbacks."""
