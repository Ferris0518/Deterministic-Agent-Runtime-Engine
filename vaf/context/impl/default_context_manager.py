"""Default context manager implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vaf.context.component import IContextManager
from vaf.context.types import Prompt, SessionContext
from vaf.model.types import Message

if TYPE_CHECKING:
    from vaf.plan.types import Task
    from vaf.memory.component import IMemory


class DefaultContextManager(IContextManager):
    """Simple context manager that maintains conversation history."""

    def __init__(self, memory: "IMemory | None" = None) -> None:
        self._memory = memory
        self._messages: list[Message] = []

    def open_session(self, task: "Task") -> SessionContext:
        """Open a new session."""
        return SessionContext(
            user_input=task.description,
            metadata={"task_id": task.task_id},
        )

    def add_message(self, message: Message) -> None:
        """Add a message to context."""
        self._messages.append(message)
        if self._memory:
            self._memory.add(message)

    def get_messages(self, max_messages: int | None = None) -> list[Message]:
        """Get conversation messages."""
        if max_messages is None:
            return list(self._messages)
        return list(self._messages[-max_messages:])

    def build_prompt(self, system_prompt: str | None = None) -> Prompt:
        """Build a prompt from current context."""
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.extend(self._messages)
        return Prompt(messages=messages)

    def clear(self) -> None:
        """Clear the context."""
        self._messages.clear()
