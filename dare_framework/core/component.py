from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

from dare_framework.core.config.config import Config

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


@runtime_checkable
class IComponent(Protocol):
    """Base lifecycle contract for pluggable components (Interface_Layer_Design_v1.1)."""

    @property
    def order(self) -> int:
        """Defines load order when composing multiple components."""
        ...

    async def init(self, config: Config | None = None, prompts: "IPromptStore | None" = None) -> None:
        """Initialize the component with resolved config and prompt store."""
        ...

    def register(self, registrar: "IComponentRegistrar") -> None:
        """Register the component with the composition registry."""
        ...

    async def close(self) -> None:
        """Release resources during shutdown."""
        ...


if TYPE_CHECKING:
    from dare_framework.core.component_register import IComponentRegistrar
    from dare_framework.core.models.prompt_store import IPromptStore
