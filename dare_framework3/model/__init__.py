"""Model domain facade (compat shim)."""

from dare_framework3.model.components import IModelAdapter
from dare_framework3.model.types import Message, ModelResponse, GenerateOptions

__all__ = ["IModelAdapter", "Message", "ModelResponse", "GenerateOptions"]
