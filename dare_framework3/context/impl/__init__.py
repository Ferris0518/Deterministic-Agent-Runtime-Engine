"""Context implementations (compat shim)."""

from dare_framework3._internal.context.impl.noop_indexer import NoOpIndexer
from dare_framework3._internal.context.impl.noop_retriever import NoOpRetriever

__all__ = ["NoOpIndexer", "NoOpRetriever"]
