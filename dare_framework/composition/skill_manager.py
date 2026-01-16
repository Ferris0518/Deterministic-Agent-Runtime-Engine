from __future__ import annotations

from dare_framework.components.registries import SkillRegistry
from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, ENTRYPOINT_SKILLS
from dare_framework.core.skill.skill import ISkill


class SkillManager(BaseComponentManager[ISkill]):
    def __init__(
        self,
        skill_registry: SkillRegistry,
        entry_points_loader: EntryPointLoader | None = None,
    ) -> None:
        super().__init__(ENTRYPOINT_SKILLS, ISkill, entry_points_loader, config_section="skills")
        self._skill_registry = skill_registry

    def _register_component(self, component: ISkill) -> None:
        self._skill_registry.register_skill(component)
