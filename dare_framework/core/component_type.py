from __future__ import annotations

from enum import Enum


class ComponentType(Enum):
    VALIDATOR = "validator"
    MEMORY = "memory"
    MODEL_ADAPTER = "model_adapter"
    TOOL = "tool"
    SKILL = "skill"
    MCP = "mcp"
    HOOK = "hook"
    PROMPT = "prompt"
