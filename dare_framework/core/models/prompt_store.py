from __future__ import annotations

from typing import runtime_checkable, Protocol

from dare_framework.core.configurable_component import IConfigurableComponent


@runtime_checkable
class IPromptStore(IConfigurableComponent, Protocol):
    """Stores prompts by name/version (Interface_Layer_Design_v1.1)."""

    def get_prompt(self, name: str, version: str | None = None) -> str:
        """Retrieve a prompt string by name and optional version."""
        ...
