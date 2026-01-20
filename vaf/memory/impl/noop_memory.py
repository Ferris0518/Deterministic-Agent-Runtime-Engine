"""No-op memory implementation."""

from __future__ import annotations

from vaf.memory.component import IMemory
from vaf.model.types import Message


class NoOpMemory(IMemory):
    """Simple in-memory message storage."""

    def __init__(self) -> None:
        self._messages: list[Message] = []

    def add(self, message: Message) -> None:
        """Add a message to memory."""
        self._messages.append(message)

    def get_messages(self, max_messages: int | None = None) -> list[Message]:
        """Get messages from memory."""
        if max_messages is None:
            return list(self._messages)
        return list(self._messages[-max_messages:])

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()
