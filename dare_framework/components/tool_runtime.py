from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dare_framework.core.interfaces import (
    IPolicyEngine,
    ISkillRegistry,
    IToolRuntime,
    IValidator,
    PolicyDecision,
)
from dare_framework.components.toolkit import BasicToolkit
from dare_framework.core.errors import PolicyDeniedError, ToolExecutionError
from dare_framework.core.models import DonePredicate, Envelope, Evidence, RunContext, ToolDefinition, ToolResult, ToolType, RiskLevel


@dataclass
class DefaultToolRuntime(IToolRuntime):
    def __init__(
        self,
        toolkit: BasicToolkit,
        policy_engine: IPolicyEngine,
        *,
        skill_registry: ISkillRegistry | None = None,
        validator: IValidator | None = None,
    ) -> None:
        self._toolkit = toolkit
        self._policy_engine = policy_engine
        self._skill_registry = skill_registry
        self._validator = validator

    async def invoke(
        self,
        name: str,
        input: dict[str, Any],
        ctx: RunContext,
        envelope: Envelope | None = None,
        done_predicate: DonePredicate | None = None,
    ) -> ToolResult:
        tool = self._toolkit.get_tool(name)
        if not tool:
            raise ToolExecutionError(f"Unknown tool: {name}")

        if envelope and envelope.allowed_tools and name not in envelope.allowed_tools:
            raise ToolExecutionError(f"Tool {name} not allowed by envelope")

        decision = self._policy_engine.check_tool_access(tool, ctx)
        if decision == PolicyDecision.DENY:
            raise PolicyDeniedError(f"Policy denied tool: {name}")

        if envelope or done_predicate:
            return await self._tool_loop(tool, input, ctx, envelope, done_predicate)

        return await tool.execute(input, ctx)

    def get_tool(self, name: str):
        return self._toolkit.get_tool(name)

    def list_tools(self) -> list[ToolDefinition]:
        definitions: list[ToolDefinition] = []
        for tool in self._toolkit.list_tools():
            definitions.append(
                ToolDefinition(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.get_input_schema(),
                    tool_type=tool.tool_type,
                    risk_level=tool.risk_level,
                    is_plan_tool=False,
                )
            )
        if self._skill_registry:
            tool_names = {tool.name for tool in self._toolkit.list_tools()}
            for skill in self._skill_registry.list_skills():
                if skill.name in tool_names:
                    continue
                definitions.append(
                    ToolDefinition(
                        name=skill.name,
                        description=skill.description,
                        input_schema=skill.get_input_schema(),
                        tool_type=ToolType.WORKUNIT,
                        risk_level=RiskLevel.READ_ONLY,
                        is_plan_tool=True,
                    )
                )
        return definitions

    def is_plan_tool(self, name: str) -> bool:
        return bool(self._skill_registry and self._skill_registry.get_skill(name))

    async def _tool_loop(
        self,
        tool,
        input: dict[str, Any],
        ctx: RunContext,
        envelope: Envelope | None,
        done_predicate: DonePredicate | None,
    ) -> ToolResult:
        evidence: list[Evidence] = []
        predicate = self._build_predicate(envelope, done_predicate)
        budget = envelope.budget if envelope else None
        attempts = 0

        while True:
            attempts += 1
            if budget and budget.exceeded():
                raise ToolExecutionError(
                    f"Tool loop for {tool.name} exceeded envelope budget after {attempts} attempts"
                )
            if budget:
                budget.record_attempt()

            result = await tool.execute(input, ctx)
            if budget:
                budget.record_tool_call()

            if result.evidence_ref:
                evidence.append(result.evidence_ref)

            if not predicate:
                if result.success:
                    return result
                continue

            if await self._predicate_satisfied(evidence, predicate):
                return result

    async def _predicate_satisfied(self, evidence: list[Evidence], predicate: DonePredicate) -> bool:
        if self._validator:
            return await self._validator.validate_evidence(evidence, predicate)
        return predicate.is_satisfied(evidence)

    def _build_predicate(
        self, envelope: Envelope | None, done_predicate: DonePredicate | None
    ) -> DonePredicate | None:
        if done_predicate:
            return done_predicate
        if envelope and envelope.required_evidence:
            return DonePredicate(
                evidence_conditions=envelope.required_evidence,
                invariant_conditions=[],
            )
        return None
