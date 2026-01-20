"""Context domain data types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dare_framework3._internal.model.types import Message


class ContextStage(Enum):
    """Context assembly stages aligned to the loop phases."""

    SESSION_OBSERVE = "session_observe"
    MILESTONE_OBSERVE = "milestone_observe"
    PLAN = "plan"
    EXECUTE = "execute"
    TOOL = "tool"
    VERIFY = "verify"


@dataclass(frozen=True)
class AssembledContext:
    """Assembled context window for the model."""

    messages: list["Message"]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Prompt:
    """Final prompt representation for model adapters."""

    messages: list["Message"]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedContext:
    """Retrieved items for context assembly."""

    items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class IndexStatus:
    """Index readiness status."""

    ready: bool = True
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContextPacket:
    """Context handoff packet."""

    id: str
    source: str
    target: str
    summary: str
    attachments: list[str] = field(default_factory=list)
    budget_attribution: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeStateView:
    """Minimal state view for context assembly."""

    task_id: str
    run_id: str
    milestone_id: str | None
    stage: ContextStage
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Session-scoped context holder."""

    user_input: str
    metadata: dict[str, Any] = field(default_factory=dict)
