"""Minimal preset for a barebones agent."""

from __future__ import annotations

from dare_framework3.presets.base import Preset


class MinimalPreset(Preset):
    """Minimal preset with no additional components."""

    name = "minimal"

    @property
    def description(self) -> str:
        return "Minimal preset with explicit wiring"
