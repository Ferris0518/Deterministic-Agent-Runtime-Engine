from __future__ import annotations

from typing import Protocol

from dare_framework.core.skill.skill import ISkill


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
