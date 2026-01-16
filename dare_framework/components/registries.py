from __future__ import annotations

from typing import Iterable

from dare_framework.core.skill.skill_registry import ISkillRegistry
from dare_framework.core.skill.skill import ISkill
from dare_framework.core.risk_level import RiskLevel
from dare_framework.core.tool.enums import ToolType
from dare_framework.core.tool.models import ToolDefinition
from dare_framework.core.tool.protocols import ITool, IToolkit, IToolRegistry


class ToolRegistry(IToolkit, IToolRegistry):
    def __init__(self) -> None:
        self._tools: dict[str, ITool] = {}

    def register_tool(self, tool: ITool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ITool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
                output_schema=tool.output_schema,
                tool_type=getattr(tool, "tool_type", ToolType.WORKUNIT if tool.is_work_unit else ToolType.ATOMIC),
                risk_level=_normalize_risk(tool.risk_level),
                requires_approval=tool.requires_approval,
                timeout_seconds=tool.timeout_seconds,
                produces_assertions=tool.produces_assertions,
                is_work_unit=tool.is_work_unit,
            )
            for tool in self._tools.values()
        ]

    def get_tool_definition(self, name: str) -> ToolDefinition | None:
        tool = self.get_tool(name)
        if tool is None:
            return None
        return ToolDefinition(
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
            tool_type=getattr(tool, "tool_type", ToolType.WORKUNIT if tool.is_work_unit else ToolType.ATOMIC),
            risk_level=_normalize_risk(tool.risk_level),
            requires_approval=tool.requires_approval,
            timeout_seconds=tool.timeout_seconds,
            produces_assertions=tool.produces_assertions,
            is_work_unit=tool.is_work_unit,
        )

    def list_tool_definitions(self) -> list[ToolDefinition]:
        return self.list_tools()

    def register_many(self, tools: Iterable[ITool]) -> None:
        for tool in tools:
            self.register_tool(tool)


class SkillRegistry(ISkillRegistry):
    def __init__(self) -> None:
        self._skills: dict[str, ISkill] = {}

    def register_skill(self, skill: ISkill) -> None:
        self._skills[skill.name] = skill

    def get_skill(self, name: str) -> ISkill | None:
        return self._skills.get(name)

    def list_skills(self) -> list[ISkill]:
        return list(self._skills.values())

    def register_many(self, skills: Iterable[ISkill]) -> None:
        for skill in skills:
            self.register_skill(skill)


def _normalize_risk(value) -> RiskLevel:
    if isinstance(value, RiskLevel):
        return value
    try:
        return RiskLevel(value)
    except ValueError:
        return RiskLevel.READ_ONLY
