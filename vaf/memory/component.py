"""Memory domain component interfaces."""

from __future__ import annotations

from typing import Any, Protocol

from vaf.model.types import Message


class IMemory(Protocol):
    """Memory interface for conversation history.
    
    Stores and retrieves conversation messages.
    """

    def add(self, message: Message) -> None:
        """Add a message to memory.
        
        Args:
            message: The message to add
        """
        ...

    def get_messages(self, max_messages: int | None = None) -> list[Message]:
        """Get messages from memory.
        
        Args:
            max_messages: Maximum number of messages to return (None = all)
            
        Returns:
            List of messages
        """
        ...

    def clear(self) -> None:
        """Clear all messages from memory."""
        ...
