from __future__ import annotations

from typing import Generic, Protocol, TypeVar, runtime_checkable, TYPE_CHECKING

from .models.config import ComponentType, Config
from .models.plan import Task
from .models.results import RunResult

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


@runtime_checkable
class IComponentRegistrar(Protocol):
    """Registers components into the composition layer (Interface_Layer_Design_v1.1)."""

    def register_component(self, component: "IComponent") -> None:
        """Attach a component to the active composition registry."""
        ...


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

    def register(self, registrar: IComponentRegistrar) -> None:
        """Register the component with the composition registry."""
        ...

    async def close(self) -> None:
        """Release resources during shutdown."""
        ...


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


class IAgent(Protocol, Generic[DepsT, OutputT]):
    """Composition-layer wrapper that drives a configured runtime (Interface_Layer_Design_v1.1)."""

    async def run(self, task: Task, deps: DepsT) -> RunResult[OutputT]:
        """Run the configured runtime with provided dependencies."""
        ...


if TYPE_CHECKING:
    from .config import IPromptStore
