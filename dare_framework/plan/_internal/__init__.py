"""Plan domain internal implementations (unstable API).

These implementations are not part of the public API and may change
without deprecation warnings. Use at your own risk.
"""

from dare_framework.plan._internal.composite_validator import CompositeValidator
from dare_framework.plan._internal.llm_planner import DEFAULT_PLANNING_PROMPT, LLMPlanner
from dare_framework.plan._internal.llm_remediator import (
    DEFAULT_REMEDIATION_PROMPT,
    LLMRemediator,
    NoOpRemediator,
    SimpleRemediator,
)
from dare_framework.plan._internal.plan_loop import (
    PlanAttemptRecord,
    PlanLoop,
    PlanLoopConfig,
    PlanLoopResult,
)
from dare_framework.plan._internal.schema_validator import (
    PermissiveValidator,
    SchemaValidator,
)
from dare_framework.plan._internal.simple_planner import (
    SequentialPlanner,
    SimplePlanner,
)

__all__ = [
    # Planners
    "LLMPlanner",
    "SimplePlanner",
    "SequentialPlanner",
    "DEFAULT_PLANNING_PROMPT",
    # Validators
    "SchemaValidator",
    "PermissiveValidator",
    "CompositeValidator",
    # Remediators
    "LLMRemediator",
    "SimpleRemediator",
    "NoOpRemediator",
    "DEFAULT_REMEDIATION_PROMPT",
    # Plan Loop
    "PlanLoop",
    "PlanLoopConfig",
    "PlanLoopResult",
    "PlanAttemptRecord",
]
