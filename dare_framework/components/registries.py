from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from dare_framework.components.interfaces import ISkill, ISkillRegistry, ITool
from dare_framework.components.toolkit import BasicToolkit


@dataclass
class ToolRegistry(BasicToolkit):
    def register_many(self, tools: Iterable[ITool]) -> None:
        for tool in tools:
            self.register_tool(tool)


@dataclass
class SkillRegistry(ISkillRegistry):
    _skills: dict[str, ISkill] = field(default_factory=dict)

    def register_skill(self, skill: ISkill) -> None:
        self._skills[skill.name] = skill

    def get_skill(self, name: str) -> ISkill | None:
        return self._skills.get(name)

    def list_skills(self) -> list[ISkill]:
        return list(self._skills.values())

    def register_many(self, skills: Iterable[ISkill]) -> None:
        for skill in skills:
            self.register_skill(skill)
