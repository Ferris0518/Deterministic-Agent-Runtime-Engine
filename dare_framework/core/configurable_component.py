from __future__ import annotations

from typing import runtime_checkable, Protocol

from dare_framework.core.component import IComponent
from dare_framework.core.component_type import ComponentType


@runtime_checkable
class IConfigurableComponent(IComponent, Protocol):
    """Entry point component with stable config identity (Interface_Layer_Design_v1.1)."""

    @property
    def component_type(self) -> ComponentType:
        """Component category used for config scoping."""
        ...

    @property
    def component_name(self) -> str:
        """Stable identifier used for config overrides and entry points."""
        ...
