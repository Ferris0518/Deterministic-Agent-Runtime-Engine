"""Preset facade for stable imports."""

from dare_framework3.presets.base import Preset
from dare_framework3.presets.minimal import MinimalPreset
from dare_framework3.presets.autogpt import AutoGPTPreset
from dare_framework3.presets.reflexion import ReflexionPreset

__all__ = ["Preset", "MinimalPreset", "AutoGPTPreset", "ReflexionPreset"]
