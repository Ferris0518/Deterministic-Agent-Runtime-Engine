"""Mock model adapter for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vaf.model.component import IModelAdapter
from vaf.model.types import Message, ModelResponse

if TYPE_CHECKING:
    from vaf.tool.types import ToolDefinition


class MockModelAdapter(IModelAdapter):
    """Mock model adapter for testing purposes.
    
    Returns predefined responses without making actual API calls.
    """

    def __init__(self, response: str = "Mock response") -> None:
        self._response = response

    async def generate(
        self,
        messages: list[Message],
        tools: list["ToolDefinition"] | None = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Return a mock response."""
        return ModelResponse(content=self._response, tool_calls=[])
