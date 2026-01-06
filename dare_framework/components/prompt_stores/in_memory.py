from __future__ import annotations

from ...core.config import IPromptStore
from ...core.models.config import ComponentType
from ..base_component import ConfigurableComponent


class InMemoryPromptStore(ConfigurableComponent, IPromptStore):
    component_type = ComponentType.PROMPT

    def __init__(self, prompts: dict[tuple[str, str | None], str] | None = None) -> None:
        self._prompts = prompts or {}

    def get_prompt(self, name: str, version: str | None = None) -> str:
        key = (name, version)
        if key in self._prompts:
            return self._prompts[key]
        fallback = (name, None)
        if fallback in self._prompts:
            return self._prompts[fallback]
        raise KeyError(f"Prompt not found: {name} ({version})")
