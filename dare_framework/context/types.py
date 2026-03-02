"""context domain types (context-centric).

Alignment note:
- Context holds references (STM/LTM/Knowledge + Budget).
- Messages are assembled request-time via `Context.assemble(...)`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from dare_framework.tool.types import CapabilityDescriptor

if TYPE_CHECKING:
    from dare_framework.model.types import Prompt


class MessageMark(str, Enum):
    """消息标记：IMMUTABLE 不可改，PERSISTENT 持久化（跨轮次保留），TEMPORARY 默认可清理。"""

    IMMUTABLE = "immutable"
    PERSISTENT = "persistent"
    TEMPORARY = "temporary"


@dataclass
class Message:
    """Unified message format."""

    role: str
    content: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    mark: MessageMark = MessageMark.TEMPORARY
    id: str | None = None


@dataclass
class Budget:
    """Resource budget = limits + usage tracking."""

    # Limits
    max_tokens: int | None = None
    max_cost: float | None = None
    max_time_seconds: int | None = None
    max_tool_calls: int | None = None

    # Usage tracking
    used_tokens: float = 0.0
    used_cost: float = 0.0
    used_time_seconds: float = 0.0
    used_tool_calls: int = 0


@dataclass
class AssembledContext:
    """Request-time context for a single LLM call."""

    messages: list[Message]
    sys_prompt: Prompt | None = None
    tools: list[CapabilityDescriptor] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = ["AssembledContext", "Budget", "Message", "MessageMark"]
