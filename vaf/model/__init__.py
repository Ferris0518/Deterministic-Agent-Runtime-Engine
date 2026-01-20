"""Model domain: LLM adapter interfaces and implementations."""

from vaf.model.component import IModelAdapter
from vaf.model.types import Message, ModelResponse
from vaf.model.impl.openai_adapter import OpenAIModelAdapter
from vaf.model.impl.mock_adapter import MockModelAdapter

__all__ = [
    "IModelAdapter",
    "Message",
    "ModelResponse",
    "OpenAIModelAdapter",
    "MockModelAdapter",
]
