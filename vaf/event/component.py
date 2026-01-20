"""Event domain component interfaces.

VAF version - includes hook interfaces (merged from hook/).
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, Sequence

from vaf.event.types import Event, HookType


# =============================================================================
# Event Log Interface
# =============================================================================

class IEventLog(Protocol):
    """Event log for audit and replay."""

    async def append(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> str:
        """Append an event to the log.
        
        Args:
            event_type: Type of event
            payload: Event data
            
        Returns:
            Event ID
        """
        ...

    async def query(
        self,
        *,
        event_type: str | None = None,
        limit: int = 100,
    ) -> Sequence[Event]:
        """Query events from the log.
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum events to return
            
        Returns:
            Matching events
        """
        ...


# =============================================================================
# Event Listener Interface
# =============================================================================

class IEventListener(Protocol):
    """Real-time event listener."""

    async def on_event(self, event: Event) -> None:
        """Handle an event.
        
        Args:
            event: The event to handle
        """
        ...


# =============================================================================
# Hook Interfaces (merged from hook/)
# =============================================================================

class IHook(Protocol):
    """Hook callback interface."""
    
    @property
    def name(self) -> str:
        """Hook name identifier."""
        ...
    
    @property
    def hook_type(self) -> HookType:
        """Type of hook (when it triggers)."""
        ...
    
    async def __call__(self, *args: Any, **kwargs: Any) -> None:
        """Execute the hook callback.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        ...


class IExtensionPoint(Protocol):
    """Extension point for registering and triggering hooks."""
    
    def register(
        self,
        hook_type: HookType,
        name: str,
        callback: Callable[..., Any],
    ) -> None:
        """Register a hook callback.
        
        Args:
            hook_type: Type of hook
            name: Unique hook name
            callback: The callback function
        """
        ...
    
    def unregister(self, hook_type: HookType, name: str) -> None:
        """Unregister a hook callback.
        
        Args:
            hook_type: Type of hook
            name: Hook name to remove
        """
        ...
    
    async def emit(self, hook_type: HookType, *args: Any, **kwargs: Any) -> None:
        """Trigger all hooks of a given type.
        
        Args:
            hook_type: Type of hook to trigger
            *args: Arguments to pass to hooks
            **kwargs: Keyword arguments to pass to hooks
        """
        ...
