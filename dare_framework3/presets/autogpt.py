"""AutoGPT-style preset placeholder."""

from __future__ import annotations

from dare_framework3.presets.base import Preset


class AutoGPTPreset(Preset):
    """Preset placeholder for AutoGPT-style composition."""

    name = "autogpt"

    @property
    def description(self) -> str:
        return "Goal-oriented preset with planning and tools"
