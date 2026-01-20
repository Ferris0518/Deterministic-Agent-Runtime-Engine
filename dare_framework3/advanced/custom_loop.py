"""Advanced entry point for custom run loops."""

from __future__ import annotations

from typing import Protocol

from dare_framework3.interfaces import IRunLoop


class CustomLoop(IRunLoop, Protocol):
    """Marker protocol for custom run loops."""

    pass
