"""Memory domain: Memory interfaces and implementations."""

from vaf.memory.component import IMemory
from vaf.memory.impl.noop_memory import NoOpMemory

__all__ = [
    "IMemory",
    "NoOpMemory",
]
