from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from dare_framework.core.component import IComponent


@runtime_checkable
class IComponentRegistrar(Protocol):
    """Registers components into the composition layer (Interface_Layer_Design_v1.1)."""

    def register_component(self, component: "IComponent") -> None:
        """Attach a component to the active composition registry."""
        ...
