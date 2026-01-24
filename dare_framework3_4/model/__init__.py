"""model domain facade."""

from dare_framework3_4.model.interfaces import IModelAdapter, IModelAdapterManager
from dare_framework3_4.model.types import Prompt, ModelResponse, GenerateOptions
from dare_framework3_4.model._internal.openai_adapter import OpenAIModelAdapter

__all__ = [
    "IModelAdapter",
    "IModelAdapterManager",
    "Prompt",
    "ModelResponse",
    "GenerateOptions",
    "OpenAIModelAdapter",
]
