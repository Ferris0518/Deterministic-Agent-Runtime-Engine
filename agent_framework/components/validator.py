from __future__ import annotations

from ..core.interfaces import IValidator
from ..core.models import DonePredicate, Milestone, PlanStep, RunContext, ValidationResult, VerifyResult


class SimpleValidator(IValidator):
    async def validate_plan(self, steps: list[PlanStep], ctx: RunContext) -> ValidationResult:
        if not steps:
            return ValidationResult(success=False, errors=["Plan has no steps"])
        return ValidationResult(success=True, errors=[])

    async def validate_milestone(self, milestone: Milestone, result, ctx: RunContext) -> VerifyResult:
        if result.success:
            return VerifyResult(success=True, errors=[], evidence={"milestone": milestone.milestone_id})
        return VerifyResult(success=False, errors=result.errors, evidence={})

    async def validate_evidence(self, evidence: dict, predicate: DonePredicate) -> bool:
        if not predicate.required_keys:
            return True
        return all(key in evidence for key in predicate.required_keys)
