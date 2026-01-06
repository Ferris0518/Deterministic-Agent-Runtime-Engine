from __future__ import annotations

from ...core.validation import IValidator
from ...core.models.config import ComponentType
from ...core.models.plan import DonePredicate, Milestone, ProposedStep, ValidationResult, VerifyResult
from ...core.models.results import ExecuteResult
from ...core.models.runtime import RunContext
from ...core.models.tool import Evidence
from ..base_component import ConfigurableComponent


class CompositeValidator(ConfigurableComponent, IValidator):
    component_type = ComponentType.VALIDATOR

    def __init__(self, validators: list[IValidator]):
        self._validators = list(validators)

    def _ordered(self) -> list[IValidator]:
        return sorted(self._validators, key=lambda validator: getattr(validator, "order", 100))

    async def validate_plan(self, proposed_steps: list[ProposedStep], ctx: RunContext) -> ValidationResult:
        errors: list[str] = []
        for validator in self._ordered():
            result = await validator.validate_plan(proposed_steps, ctx)
            if not result.success:
                errors.extend(result.errors)
        return ValidationResult(success=not errors, errors=errors)

    async def validate_milestone(
        self,
        milestone: Milestone,
        result: ExecuteResult,
        ctx: RunContext,
    ) -> VerifyResult:
        errors: list[str] = []
        evidence: list[Evidence] = []
        success = True
        for validator in self._ordered():
            verify_result = await validator.validate_milestone(milestone, result, ctx)
            if not verify_result.success:
                success = False
                errors.extend(verify_result.errors)
            evidence.extend(verify_result.evidence)
        return VerifyResult(success=success, errors=errors, evidence=evidence)

    async def validate_evidence(self, evidence: list[Evidence], predicate: DonePredicate) -> bool:
        results = [
            await validator.validate_evidence(evidence, predicate)
            for validator in self._ordered()
        ]
        return all(results)
