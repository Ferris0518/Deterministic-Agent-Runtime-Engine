"""Context domain component interfaces.

VAF simplified version - only essential interfaces retained.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from vaf.context.types import Prompt, SessionContext
from vaf.model.types import Message

if TYPE_CHECKING:
    from vaf.plan.types import Task


class IContextManager(Protocol):
    """Context management interface.
    
    Manages conversation context and prompt assembly.
    """

    def open_session(self, task: "Task") -> SessionContext:
        """Open a new session for the given task.
        
        Args:
            task: The task to create a session for
            
        Returns:
            A SessionContext for tracking session state
        """
        ...

    def add_message(self, message: Message) -> None:
        """Add a message to the context.
        
        Args:
            message: The message to add
        """
        ...
    
    def get_messages(self, max_messages: int | None = None) -> list[Message]:
        """Get conversation messages.
        
        Args:
            max_messages: Maximum number of messages to return (None = all)
            
        Returns:
            List of messages
        """
        ...

    def build_prompt(self, system_prompt: str | None = None) -> Prompt:
        """Build a prompt from current context.
        
        Args:
            system_prompt: Optional system prompt to prepend
            
        Returns:
            The assembled prompt
        """
        ...
    
    def clear(self) -> None:
        """Clear the context."""
        ...
