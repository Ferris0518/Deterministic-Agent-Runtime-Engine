from __future__ import annotations

from typing import Protocol, runtime_checkable

from dare_framework.core.plan.models import (
    DonePredicate,
    Milestone,
    ProposedStep,
    ValidationResult,
    VerifyResult,
)
from dare_framework.core.context.models import ExecuteResult, RunContext
from dare_framework.core.models.evidence import Evidence
from dare_framework.core.configurable_component import IConfigurableComponent


@runtime_checkable
class IValidator(IConfigurableComponent, Protocol):
    """Validates plans, milestones, and evidence per the trust model (Architecture_Final_Review_v1.3)."""

    async def validate_plan(self, proposed_steps: list[ProposedStep], ctx: RunContext) -> ValidationResult:
        """Validate proposed steps before execution."""
        ...

    async def validate_milestone(
        self,
        milestone: Milestone,
        execute_result: ExecuteResult,
        ctx: RunContext,
    ) -> VerifyResult:
        """Validate milestone completion after execution."""
        ...

    async def validate_evidence(self, evidence: list[Evidence], predicate: DonePredicate) -> bool:
        """Verify evidence against the done predicate."""
        ...
