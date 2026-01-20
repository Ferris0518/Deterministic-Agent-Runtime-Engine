"""Stable component interfaces (Layer 2)."""

from dare_framework3._internal.execution.components import IHook
from dare_framework3._internal.context.components import (
    IContextStrategy,
    IMemory,
    IPromptStore,
    IRetriever,
    IIndexer,
)
from dare_framework3._internal.security.components import ITrustVerifier, IPolicyEngine, ISandbox
from dare_framework3._internal.tool.components import ITool, ICapabilityProvider, ISkill
from dare_framework3._internal.plan.components import IPlanner, IValidator, IRemediator
from dare_framework3._internal.model.components import IModelAdapter

__all__ = [
    "IHook",
    "IContextStrategy",
    "IMemory",
    "IPromptStore",
    "IRetriever",
    "IIndexer",
    "ITrustVerifier",
    "IPolicyEngine",
    "ISandbox",
    "ITool",
    "ICapabilityProvider",
    "ISkill",
    "IPlanner",
    "IValidator",
    "IRemediator",
    "IModelAdapter",
]
