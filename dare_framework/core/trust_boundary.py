from __future__ import annotations

from typing import Protocol

from .models.plan import ProposedPlan, ProposedStep, ValidatedPlan, ValidatedStep
from .registries import IToolRegistry


class ITrustBoundary(Protocol):
    """Derives trusted fields before policy enforcement (Architecture_Final_Review_v1.3)."""

    def derive_step(self, proposed_step: ProposedStep, registry: IToolRegistry) -> ValidatedStep:
        """Return a validated step derived from trusted tool metadata."""
        ...

    def derive_plan(self, proposed_plan: ProposedPlan, registry: IToolRegistry) -> ValidatedPlan:
        """Return a validated plan derived from trusted tool metadata."""
        ...
