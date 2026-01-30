"""Tests for PlanLoop."""

from __future__ import annotations

import pytest

from dare_framework.plan._internal.plan_loop import (
    PlanAttemptRecord,
    PlanLoop,
    PlanLoopConfig,
    PlanLoopResult,
)
from dare_framework.plan.interfaces import IPlanner, IRemediator, IValidator
from dare_framework.plan.types import (
    Milestone,
    ProposedPlan,
    ProposedStep,
    ValidatedPlan,
    ValidatedStep,
    VerifyResult,
)
from dare_framework.security.types import RiskLevel


class MockPlanner(IPlanner):
    """Mock planner for testing."""

    def __init__(self, plans: list[ProposedPlan] | None = None) -> None:
        self._plans = plans or []
        self._index = 0
        self.call_count = 0

    @property
    def name(self) -> str:
        return "mock_planner"

    @property
    def component_type(self):
        from dare_framework.infra.component import ComponentType
        return ComponentType.PLANNER

    async def plan(self, ctx: Any) -> ProposedPlan:
        self.call_count += 1
        if self._index < len(self._plans):
            plan = self._plans[self._index]
            self._index += 1
            return plan
        return ProposedPlan(plan_description="Default", steps=[])


class MockValidator(IValidator):
    """Mock validator for testing."""

    def __init__(self, results: list[ValidatedPlan] | None = None) -> None:
        self._results = results or []
        self._index = 0
        self.call_count = 0
        self.last_plan: ProposedPlan | None = None

    @property
    def name(self) -> str:
        return "mock_validator"

    @property
    def component_type(self):
        from dare_framework.infra.component import ComponentType
        return ComponentType.VALIDATOR

    async def validate_plan(self, plan: ProposedPlan, ctx: Any) -> ValidatedPlan:
        self.call_count += 1
        self.last_plan = plan
        if self._index < len(self._results):
            result = self._results[self._index]
            self._index += 1
            return result
        return ValidatedPlan(plan_description=plan.plan_description, steps=[], success=True)

    async def verify_milestone(self, result: Any, ctx: Any) -> VerifyResult:
        return VerifyResult(success=True)


class MockRemediator(IRemediator):
    """Mock remediator for testing."""

    def __init__(self, reflections: list[str] | None = None) -> None:
        self._reflections = reflections or []
        self._index = 0
        self.call_count = 0

    @property
    def name(self) -> str:
        return "mock_remediator"

    @property
    def component_type(self):
        from dare_framework.infra.component import ComponentType
        return ComponentType.REMEDIATOR

    async def remediate(self, verify_result: VerifyResult, ctx: Any) -> str:
        self.call_count += 1
        if self._index < len(self._reflections):
            reflection = self._reflections[self._index]
            self._index += 1
            return reflection
        return "Default reflection"


class MockEventLog:
    """Mock event log for testing."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    async def append(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


class TestPlanLoop:
    """Tests for PlanLoop."""

    async def test_success_on_first_attempt(self, mock_context: Any) -> None:
        """Test successful plan generation on first attempt."""
        planner = MockPlanner()
        validator = MockValidator()
        loop = PlanLoop(planner=planner, validator=validator)

        milestone = Milestone(
            milestone_id="m_001",
            description="Test milestone",
        )

        result = await loop.run(milestone, mock_context)

        assert result.success is True
        assert result.validated_plan is not None
        assert len(result.attempts) == 1
        assert planner.call_count == 1
        assert validator.call_count == 1

    async def test_retry_on_validation_failure(self, mock_context: Any) -> None:
        """Test that loop retries on validation failure."""
        planner = MockPlanner([
            ProposedPlan(plan_description="First attempt", steps=[]),
            ProposedPlan(plan_description="Second attempt", steps=[]),
        ])
        validator = MockValidator([
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error 1"]),
            ValidatedPlan(plan_description="Success", steps=[], success=True),
        ])
        loop = PlanLoop(planner=planner, validator=validator)

        milestone = Milestone(milestone_id="m_001", description="Test")
        result = await loop.run(milestone, mock_context)

        assert result.success is True
        assert planner.call_count == 2
        assert validator.call_count == 2
        assert len(result.attempts) == 2

    async def test_max_attempts_exhausted(self, mock_context: Any) -> None:
        """Test failure when max attempts exhausted."""
        planner = MockPlanner()
        validator = MockValidator([
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error"]),
        ] * 5)
        loop = PlanLoop(
            planner=planner,
            validator=validator,
            config=PlanLoopConfig(max_attempts=3),
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        result = await loop.run(milestone, mock_context)

        assert result.success is False
        assert result.validated_plan is None
        assert len(result.attempts) == 3
        assert planner.call_count == 3

    async def test_plan_attempt_isolation(self, mock_context: Any) -> None:
        """Test that failed attempts don't contaminate context state."""
        planner = MockPlanner()
        validator = MockValidator([
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error"]),
            ValidatedPlan(plan_description="Success", steps=[], success=True),
        ])
        remediator = MockRemediator(["Reflection 1"])
        loop = PlanLoop(
            planner=planner,
            validator=validator,
            remediator=remediator,
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        result = await loop.run(milestone, mock_context)

        # Check that reflection was added to context for second attempt
        assert mock_context.config.get("previous_reflection") == "Reflection 1"

    async def test_event_log_entries(self, mock_context: Any) -> None:
        """Test that events are logged correctly."""
        event_log = MockEventLog()
        planner = MockPlanner()
        validator = MockValidator()
        loop = PlanLoop(
            planner=planner,
            validator=validator,
            event_log=event_log,
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        await loop.run(milestone, mock_context)

        # Should have attempt and validated events
        event_types = [e[0] for e in event_log.events]
        assert "plan.attempt" in event_types
        assert "plan.validated" in event_types

    async def test_event_log_on_failure(self, mock_context: Any) -> None:
        """Test event logging on plan failure."""
        event_log = MockEventLog()
        planner = MockPlanner()
        validator = MockValidator([
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error"]),
        ])
        loop = PlanLoop(
            planner=planner,
            validator=validator,
            event_log=event_log,
            config=PlanLoopConfig(max_attempts=1),
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        await loop.run(milestone, mock_context)

        event_types = [e[0] for e in event_log.events]
        assert "plan.attempt" in event_types
        assert "plan.invalid" in event_types
        assert "plan.failed" in event_types

    async def test_remediator_called_on_failure(self, mock_context: Any) -> None:
        """Test that remediator is called on validation failure."""
        planner = MockPlanner()
        validator = MockValidator([
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error"]),
            ValidatedPlan(plan_description="Success", steps=[], success=True),
        ])
        remediator = MockRemediator(["Reflection 1"])
        loop = PlanLoop(
            planner=planner,
            validator=validator,
            remediator=remediator,
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        await loop.run(milestone, mock_context)

        assert remediator.call_count == 1

    async def test_remediator_disabled(self, mock_context: Any) -> None:
        """Test that remediator is not called when disabled."""
        planner = MockPlanner()
        validator = MockValidator([
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error"]),
            ValidatedPlan(plan_description="Success", steps=[], success=True),
        ])
        remediator = MockRemediator()
        loop = PlanLoop(
            planner=planner,
            validator=validator,
            remediator=remediator,
            config=PlanLoopConfig(enable_reflection=False),
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        await loop.run(milestone, mock_context)

        assert remediator.call_count == 0

    async def test_exception_handling(self, mock_context: Any) -> None:
        """Test handling of planner/validator exceptions."""
        class FailingPlanner(IPlanner):
            @property
            def name(self) -> str:
                return "failing_planner"
            @property
            def component_type(self):
                from dare_framework.infra.component import ComponentType
                return ComponentType.PLANNER
            async def plan(self, ctx: Any) -> ProposedPlan:
                raise ValueError("Planner failed")

        event_log = MockEventLog()
        loop = PlanLoop(
            planner=FailingPlanner(),
            validator=MockValidator(),
            event_log=event_log,
            config=PlanLoopConfig(max_attempts=1),
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        result = await loop.run(milestone, mock_context)

        assert result.success is False
        assert len(result.attempts) == 1
        assert "Planner failed" in result.attempts[0].validation_errors[0]
        assert any(e[0] == "plan.error" for e in event_log.events)

    async def test_final_reflection_compilation(self, mock_context: Any) -> None:
        """Test that final reflection is compiled from all attempts."""
        planner = MockPlanner()
        validator = MockValidator([
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error 1"]),
            ValidatedPlan(plan_description="Failed", steps=[], success=False, errors=["Error 2"]),
        ])
        remediator = MockRemediator(["Reflection 1", "Reflection 2"])
        loop = PlanLoop(
            planner=planner,
            validator=validator,
            remediator=remediator,
            config=PlanLoopConfig(max_attempts=2),
        )

        milestone = Milestone(milestone_id="m_001", description="Test")
        result = await loop.run(milestone, mock_context)

        assert result.final_reflection is not None
        assert "2 attempts" in result.final_reflection
        assert "Reflection 1" in result.final_reflection
        assert "Reflection 2" in result.final_reflection


class TestPlanLoopConfig:
    """Tests for PlanLoopConfig."""

    async def test_default_config(self) -> None:
        """Test default configuration values."""
        config = PlanLoopConfig()

        assert config.max_attempts == 3
        assert config.enable_reflection is True

    async def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = PlanLoopConfig(max_attempts=5, enable_reflection=False)

        assert config.max_attempts == 5
        assert config.enable_reflection is False


class TestPlanLoopResult:
    """Tests for PlanLoopResult."""

    async def test_success_result(self) -> None:
        """Test successful result structure."""
        validated = ValidatedPlan(plan_description="Test", steps=[], success=True)
        result = PlanLoopResult(
            validated_plan=validated,
            success=True,
        )

        assert result.success is True
        assert result.validated_plan == validated

    async def test_failure_result(self) -> None:
        """Test failure result structure."""
        attempts = [
            PlanAttemptRecord(attempt_number=0, validation_errors=["Error"]),
        ]
        result = PlanLoopResult(
            validated_plan=None,
            attempts=attempts,
            success=False,
            final_reflection="Summary",
        )

        assert result.success is False
        assert result.validated_plan is None
        assert len(result.attempts) == 1
        assert result.final_reflection == "Summary"


# Import fixtures
pytest_plugins = ["tests.unit.plan.conftest"]
