from __future__ import annotations

from typing import Protocol

from .models.tool import ToolDefinition
from .tooling import ISkill


class IToolRegistry(Protocol):
    """Trusted registry of tool metadata for validation and policy checks (Architecture_Final_Review_v1.3)."""

    def get_tool_definition(self, name: str) -> ToolDefinition | None:
        """Return the trusted tool definition for a given tool name."""
        ...

    def list_tool_definitions(self) -> list[ToolDefinition]:
        """Return all trusted tool definitions."""
        ...


class ISkillRegistry(Protocol):
    """Registry for plan-time skills (Interface_Layer_Design_v1.1)."""

    def register_skill(self, skill: ISkill) -> None:
        """Register a skill instance by name."""
        ...

    def get_skill(self, name: str) -> ISkill | None:
        """Retrieve a skill by name."""
        ...

    def list_skills(self) -> list[ISkill]:
        """List all registered skills."""
        ...
