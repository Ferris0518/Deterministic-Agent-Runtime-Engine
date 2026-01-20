"""Execution domain component interfaces."""

from __future__ import annotations

from typing import Any, Protocol

from dare_framework3._internal.execution.types import HookPhase


class IHook(Protocol):
    """A single hook callback bound to a Kernel phase."""

    @property
    def phase(self) -> HookPhase:
        ...

    def __call__(self, payload: dict[str, Any]) -> Any:
        ...
