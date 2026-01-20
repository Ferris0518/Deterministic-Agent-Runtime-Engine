"""Reflexion-style preset placeholder."""

from __future__ import annotations

from dare_framework3.presets.base import Preset


class ReflexionPreset(Preset):
    """Preset placeholder for reflection-driven execution."""

    name = "reflexion"

    @property
    def description(self) -> str:
        return "Reflection-driven preset for iterative improvement"
