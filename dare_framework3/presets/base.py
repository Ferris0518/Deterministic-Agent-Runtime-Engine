"""Preset base class for builder configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dare_framework3.builder.builder import AgentBuilder


class Preset:
    """Base preset that can configure an AgentBuilder."""

    name = "base"

    @property
    def description(self) -> str:
        return "Base preset"

    def configure(self, builder: "AgentBuilder") -> "AgentBuilder":
        return builder
