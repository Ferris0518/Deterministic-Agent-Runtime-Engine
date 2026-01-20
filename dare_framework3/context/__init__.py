"""Context domain facade (compat shim)."""

from dare_framework3.context.kernel import IContextManager
from dare_framework3.context.components import (
    IContextStrategy,
    IMemory,
    IPromptStore,
    IRetriever,
    IIndexer,
)
from dare_framework3.context.types import (
    AssembledContext,
    Prompt,
    RetrievedContext,
    IndexStatus,
    ContextPacket,
    ContextStage,
    RuntimeStateView,
    SessionContext,
)

__all__ = [
    "IContextManager",
    "IContextStrategy",
    "IMemory",
    "IPromptStore",
    "IRetriever",
    "IIndexer",
    "AssembledContext",
    "Prompt",
    "RetrievedContext",
    "IndexStatus",
    "ContextPacket",
    "ContextStage",
    "RuntimeStateView",
    "SessionContext",
]
