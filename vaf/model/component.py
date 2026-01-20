"""Model domain component interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from vaf.model.types import Message, ModelResponse

if TYPE_CHECKING:
    from vaf.tool.types import ToolDefinition


@runtime_checkable
class IModelAdapter(Protocol):
    """Model adapter for LLM inference.
    
    Translates between the framework's message format and LLM provider APIs.
    """

    async def generate(
        self,
        messages: list[Message],
        tools: list["ToolDefinition"] | None = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Generate a response from the model.
        
        Args:
            messages: The conversation history
            tools: Optional list of tool definitions
            **kwargs: Additional generation options
            
        Returns:
            The model's response, potentially including tool calls
        """
        ...
