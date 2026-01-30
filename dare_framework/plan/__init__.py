"""plan domain facade.

The plan domain provides:
- Task/Milestone/Plan/Result types for structuring work
- IPlanner interface for generating plans
- IValidator interface for validating plans and verifying milestones
- IRemediator interface for generating guidance on failures
- Default implementations (unstable) under _internal/
"""

from dare_framework.plan.interfaces import (
    IPlanner,
    IPlannerManager,
    IRemediator,
    IRemediatorManager,
    IValidator,
    IValidatorManager,
)
from dare_framework.plan.types import (
    DonePredicate,
    Envelope,
    Milestone,
    ProposedPlan,
    ProposedStep,
    RunResult,
    Task,
    ToolLoopRequest,
    ValidatedPlan,
    ValidatedStep,
    VerifyResult,
)

# Export commonly used internal implementations
# Note: These are convenience exports; direct imports from _internal
# are also supported but marked as unstable
from dare_framework.plan._internal import (
    # Planners
    LLMPlanner,
    SimplePlanner,
    SequentialPlanner,
    # Validators
    SchemaValidator,
    PermissiveValidator,
    CompositeValidator,
    # Remediators
    LLMRemediator,
    SimpleRemediator,
    NoOpRemediator,
    # Plan Loop
    PlanLoop,
    PlanLoopConfig,
    PlanLoopResult,
)

__all__ = [
    # Interfaces
    "IPlanner",
    "IPlannerManager",
    "IRemediator",
    "IRemediatorManager",
    "IValidator",
    "IValidatorManager",
    # Types
    "DonePredicate",
    "Envelope",
    "Milestone",
    "ProposedPlan",
    "ProposedStep",
    "RunResult",
    "Task",
    "ToolLoopRequest",
    "ValidatedPlan",
    "ValidatedStep",
    "VerifyResult",
    # Implementations
    "LLMPlanner",
    "SimplePlanner",
    "SequentialPlanner",
    "SchemaValidator",
    "PermissiveValidator",
    "CompositeValidator",
    "LLMRemediator",
    "SimpleRemediator",
    "NoOpRemediator",
    "PlanLoop",
    "PlanLoopConfig",
    "PlanLoopResult",
]
