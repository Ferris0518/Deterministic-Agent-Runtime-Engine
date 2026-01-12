from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MemoryItem:
    key: str
    value: str
    metadata: dict[str, Any] = field(default_factory=dict)
