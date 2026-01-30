"""Plan Loop implementation - Layer 3 of the five-layer architecture.

The Plan Loop is responsible for:
1. Generating plans using the configured IPlanner
2. Validating plans using the configured IValidator(s)
3. Isolating failed plan attempts (they don't pollute outer state)
4. Recording plan attempts to EventLog for audit
5. Handling remediation for failed attempts

Key constraint: Plan Attempt Isolation
- Failed plan attempts must not contaminate milestone/session state
- Only validated plans may proceed to execution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dare_framework.context.kernel import IContext
from dare_framework.plan.interfaces import IPlanner, IRemediator, IValidator
from dare_framework.plan.types import (
    Milestone,
    ProposedPlan,
    ValidatedPlan,
    VerifyResult,
)

if TYPE_CHECKING:
    from dare_framework.event.kernel import IEventLog


@dataclass
class PlanLoopConfig:
    """Configuration for the Plan Loop."""

    max_attempts: int = 3
    enable_reflection: bool = True


@dataclass
class PlanAttemptRecord:
    """Record of a single plan attempt (for isolation/audit)."""

    attempt_number: int
    proposed_plan: ProposedPlan | None = None
    validation_errors: list[str] = field(default_factory=list)
    reflection: str | None = None


@dataclass
class PlanLoopResult:
    """Result of the Plan Loop execution."""

    validated_plan: ValidatedPlan | None = None
    attempts: list[PlanAttemptRecord] = field(default_factory=list)
    success: bool = False
    final_reflection: str | None = None


class PlanLoop:
    """Plan Loop - generates and validates plans with attempt isolation.

    The Plan Loop ensures that:
    - Plans are validated before execution
    - Failed attempts are isolated and recorded
    - Remediation guidance is collected for retries
    - Only validated plans proceed to execution
    """

    def __init__(
        self,
        planner: IPlanner,
        validator: IValidator,
        remediator: IRemediator | None = None,
        event_log: IEventLog | None = None,
        config: PlanLoopConfig | None = None,
    ) -> None:
        """Initialize the Plan Loop.

        Args:
            planner: The planner to generate plans
            validator: The validator to check plans
            remediator: Optional remediator for failure guidance
            event_log: Optional event log for audit
            config: Optional loop configuration
        """
        self._planner = planner
        self._validator = validator
        self._remediator = remediator
        self._event_log = event_log
        self._config = config or PlanLoopConfig()

    async def run(
        self,
        milestone: Milestone,
        ctx: IContext,
    ) -> PlanLoopResult:
        """Run the Plan Loop to generate a validated plan.

        Args:
            milestone: The milestone to plan for
            ctx: The execution context

        Returns:
            PlanLoopResult containing the validated plan or failure info
        """
        attempts: list[PlanAttemptRecord] = []

        # Configure context with milestone info
        ctx.config_update({
            "milestone_id": milestone.milestone_id,
            "milestone_description": milestone.description,
            "task_description": milestone.user_input or milestone.description,
        })

        for attempt in range(self._config.max_attempts):
            # Update attempt number in context
            ctx.config_update({"plan_attempt": attempt})

            # Create attempt record
            attempt_record = PlanAttemptRecord(attempt_number=attempt)

            # Log attempt start
            await self._log_event(
                "plan.attempt",
                {
                    "milestone_id": milestone.milestone_id,
                    "attempt": attempt,
                    "max_attempts": self._config.max_attempts,
                },
            )

            try:
                # Step 1: Generate plan
                proposed = await self._planner.plan(ctx)
                attempt_record.proposed_plan = proposed

                # Step 2: Validate plan
                validated = await self._validator.validate_plan(proposed, ctx)

                if validated.success:
                    # Success! Record and return
                    await self._log_event(
                        "plan.validated",
                        {
                            "milestone_id": milestone.milestone_id,
                            "attempt": attempt,
                            "step_count": len(validated.steps),
                        },
                    )

                    return PlanLoopResult(
                        validated_plan=validated,
                        attempts=attempts + [attempt_record],
                        success=True,
                    )

                # Validation failed - record errors
                attempt_record.validation_errors = validated.errors

                await self._log_event(
                    "plan.invalid",
                    {
                        "milestone_id": milestone.milestone_id,
                        "attempt": attempt,
                        "errors": validated.errors,
                    },
                )

                # Step 3: Get remediation guidance (if enabled)
                if self._config.enable_reflection and self._remediator:
                    # Create a VerifyResult from validation errors
                    verify_result = VerifyResult(
                        success=False,
                        errors=validated.errors,
                        metadata={"stage": "validation", "attempt": attempt},
                    )

                    reflection = await self._remediator.remediate(verify_result, ctx)
                    attempt_record.reflection = reflection

                    # Update context with reflection for next attempt
                    if reflection:
                        ctx.config_update({"previous_reflection": reflection})

                attempts.append(attempt_record)

            except Exception as e:
                # Handle planner/validator exceptions
                error_msg = f"Plan loop exception: {type(e).__name__}: {str(e)}"
                attempt_record.validation_errors.append(error_msg)
                attempts.append(attempt_record)

                await self._log_event(
                    "plan.error",
                    {
                        "milestone_id": milestone.milestone_id,
                        "attempt": attempt,
                        "error": error_msg,
                    },
                )

        # All attempts exhausted
        await self._log_event(
            "plan.failed",
            {
                "milestone_id": milestone.milestone_id,
                "attempts": len(attempts),
                "reason": "max_attempts_exhausted",
            },
        )

        # Compile final reflection from all attempts
        final_reflection = self._compile_final_reflection(attempts)

        return PlanLoopResult(
            validated_plan=None,
            attempts=attempts,
            success=False,
            final_reflection=final_reflection,
        )

    async def _log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Log an event if event log is available."""
        if self._event_log is not None:
            try:
                await self._event_log.append(event_type, payload)
            except Exception:
                # Event logging should not break the loop
                pass

    def _compile_final_reflection(self, attempts: list[PlanAttemptRecord]) -> str:
        """Compile a final reflection from all failed attempts."""
        parts: list[str] = []

        parts.append(f"Plan generation failed after {len(attempts)} attempts.")
        parts.append("")

        for attempt in attempts:
            parts.append(f"Attempt {attempt.attempt_number + 1}:")

            if attempt.validation_errors:
                parts.append("  Errors:")
                for error in attempt.validation_errors:
                    parts.append(f"    - {error}")

            if attempt.reflection:
                parts.append(f"  Reflection: {attempt.reflection}")

            parts.append("")

        return "\n".join(parts)


__all__ = [
    "PlanLoop",
    "PlanLoopConfig",
    "PlanLoopResult",
    "PlanAttemptRecord",
]
