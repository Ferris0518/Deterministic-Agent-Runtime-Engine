"""Context component interfaces (compat shim)."""

from dare_framework3._internal.context.components import (
    IContextStrategy,
    IMemory,
    IPromptStore,
    IRetriever,
    IIndexer,
)

__all__ = [
    "IContextStrategy",
    "IMemory",
    "IPromptStore",
    "IRetriever",
    "IIndexer",
]
