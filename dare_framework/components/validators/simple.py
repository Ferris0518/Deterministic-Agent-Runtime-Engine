from __future__ import annotations

from ...core.validation import IValidator
from ...core.models.config import ComponentType
from ...core.models.plan import DonePredicate, Milestone, ProposedStep, ValidationResult, VerifyResult
from ...core.models.results import ExecuteResult
from ...core.models.runtime import RunContext
from ...core.models.tool import Evidence
from ..base_component import ConfigurableComponent


class SimpleValidator(ConfigurableComponent, IValidator):
    component_type = ComponentType.VALIDATOR

    async def validate_plan(self, proposed_steps: list[ProposedStep], ctx: RunContext) -> ValidationResult:
        if not proposed_steps:
            return ValidationResult(success=False, errors=["Plan has no steps"])
        return ValidationResult(success=True, errors=[])

    async def validate_milestone(
        self,
        milestone: Milestone,
        result: ExecuteResult,
        ctx: RunContext,
    ) -> VerifyResult:
        if result.success:
            return VerifyResult(success=True, errors=[], evidence=[])
        return VerifyResult(success=False, errors=result.errors, evidence=[])

    async def validate_evidence(self, evidence: list[Evidence], predicate: DonePredicate) -> bool:
        if not predicate.required_keys and not predicate.evidence_conditions:
            return True
        if predicate.required_keys:
            available_keys = set()
            for item in evidence:
                if isinstance(item.payload, dict):
                    available_keys.update(item.payload.keys())
            if not set(predicate.required_keys).issubset(available_keys):
                return False
        if predicate.evidence_conditions:
            checks = [condition.check(evidence) for condition in predicate.evidence_conditions]
            return all(checks) if predicate.require_all else any(checks)
        return True
