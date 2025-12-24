from __future__ import annotations

from typing import Iterable

from ..core.interfaces import IModelAdapter
from ..core.models import Message, ModelResponse


class MockModelAdapter(IModelAdapter):
    def __init__(self, responses: Iterable[str] | None = None):
        self._responses = list(responses or ["ok"])
        self._index = 0

    async def generate(self, messages: list[Message], tools) -> ModelResponse:
        if not self._responses:
            return ModelResponse(content="")
        response = self._responses[min(self._index, len(self._responses) - 1)]
        self._index += 1
        return ModelResponse(content=response, tool_calls=[])
