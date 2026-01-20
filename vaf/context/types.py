"""Context domain data types.

VAF simplified version - only essential types retained.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vaf.model.types import Message


# =============================================================================
# Budget and Resources
# =============================================================================

class ResourceType(Enum):
    """Resource types for budget accounting.
    
    Values:
        TOKENS: LLM tokens
        COST: Monetary cost
        TIME_SECONDS: Wall clock time
        TOOL_CALLS: Number of tool invocations
    """
    TOKENS = "tokens"
    COST = "cost"
    TIME_SECONDS = "time_seconds"
    TOOL_CALLS = "tool_calls"


@dataclass(frozen=True)
class Budget:
    """Resource budget constraints.
    
    Attributes:
        max_tokens: Maximum tokens allowed
        max_cost: Maximum cost allowed
        max_time_seconds: Maximum execution time
        max_tool_calls: Maximum tool invocations
    """
    max_tokens: int | None = None
    max_cost: float | None = None
    max_time_seconds: int | None = None
    max_tool_calls: int | None = None


# =============================================================================
# Context Stage
# =============================================================================

class ContextStage(Enum):
    """Context assembly stages.
    
    Each stage corresponds to a different phase in the agent's
    execution cycle, requiring different context composition.
    """
    OBSERVE = "observe"
    PLAN = "plan"
    EXECUTE = "execute"
    TOOL = "tool"
    VERIFY = "verify"


# =============================================================================
# Prompt
# =============================================================================

@dataclass(frozen=True)
class Prompt:
    """A prompt for model adapters.
    
    Attributes:
        messages: The conversation messages
        metadata: Additional prompt metadata
    """
    messages: list["Message"]
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Session Context
# =============================================================================

@dataclass
class SessionContext:
    """A session-scoped context holder.
    
    Attributes:
        user_input: The initial user input
        metadata: Session metadata
    """
    user_input: str
    metadata: dict[str, Any] = field(default_factory=dict)
