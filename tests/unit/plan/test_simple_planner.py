"""Tests for SimplePlanner and SequentialPlanner."""

from __future__ import annotations

import pytest

from dare_framework.infra.component import ComponentType
from dare_framework.plan._internal.simple_planner import (
    SequentialPlanner,
    SimplePlanner,
)


class TestSimplePlanner:
    """Tests for SimplePlanner."""

    async def test_name_and_component_type(self) -> None:
        """Test that planner has correct name and component type."""
        planner = SimplePlanner(default_capability_id="test_cap")

        assert planner.name == "simple_planner"
        assert planner.component_type == ComponentType.PLANNER

    async def test_custom_name(self) -> None:
        """Test that custom name is respected."""
        planner = SimplePlanner(default_capability_id="test_cap", name="custom_planner")

        assert planner.name == "custom_planner"

    async def test_plan_generation(self, mock_context: Any) -> None:
        """Test that plan is generated correctly."""
        planner = SimplePlanner(default_capability_id="test_capability")
        mock_context.config_update({
            "task_description": "Do something important",
            "milestone_id": "milestone_123",
        })

        plan = await planner.plan(mock_context)

        assert plan.plan_description == "Execute: Do something important"
        assert len(plan.steps) == 1
        assert plan.steps[0].capability_id == "test_capability"
        assert plan.steps[0].step_id == "milestone_123_step_1"
        assert plan.steps[0].description == "Do something important"
        assert plan.metadata["planner"] == "simple"

    async def test_plan_uses_milestone_description(self, mock_context: Any) -> None:
        """Test that plan uses milestone description when available."""
        planner = SimplePlanner(default_capability_id="cap")
        mock_context.config_update({
            "task_description": "Task description",
            "milestone_description": "Milestone description",
            "milestone_id": "m_001",
        })

        plan = await planner.plan(mock_context)

        assert "Milestone description" in plan.plan_description
        assert plan.steps[0].description == "Milestone description"

    async def test_plan_includes_attempt_number(self, mock_context: Any) -> None:
        """Test that plan includes attempt number from context."""
        planner = SimplePlanner(default_capability_id="cap")
        mock_context.config_update({
            "task_description": "Task",
            "plan_attempt": 2,
        })

        plan = await planner.plan(mock_context)

        assert plan.attempt == 2


class TestSequentialPlanner:
    """Tests for SequentialPlanner."""

    async def test_name_and_component_type(self) -> None:
        """Test that planner has correct name and component type."""
        planner = SequentialPlanner()

        assert planner.name == "sequential_planner"
        assert planner.component_type == ComponentType.PLANNER

    async def test_plan_with_configured_steps(self, mock_context: Any) -> None:
        """Test plan generation with configured steps."""
        steps_config = [
            {
                "capability_id": "cap_1",
                "params": {"key1": "value1"},
                "description": "First step",
            },
            {
                "capability_id": "cap_2",
                "params": {"key2": "value2"},
                "description": "Second step",
            },
        ]
        planner = SequentialPlanner(steps_config=steps_config)
        mock_context.config_update({
            "task_description": "Multi-step task",
            "milestone_id": "m_001",
        })

        plan = await planner.plan(mock_context)

        assert len(plan.steps) == 2
        assert plan.steps[0].capability_id == "cap_1"
        assert plan.steps[0].step_id == "m_001_step_1"
        assert plan.steps[0].params == {"key1": "value1"}
        assert plan.steps[0].description == "First step"

        assert plan.steps[1].capability_id == "cap_2"
        assert plan.steps[1].step_id == "m_001_step_2"
        assert plan.steps[1].description == "Second step"

        assert plan.metadata["step_count"] == 2

    async def test_plan_with_no_steps_creates_noop(self, mock_context: Any) -> None:
        """Test that planner creates a noop step when no steps configured."""
        planner = SequentialPlanner(steps_config=[])
        mock_context.config_update({
            "task_description": "Task",
            "milestone_id": "m_001",
        })

        plan = await planner.plan(mock_context)

        assert len(plan.steps) == 1
        assert plan.steps[0].capability_id == "noop"
        assert plan.steps[0].description == "No-op step"

    async def test_step_numbering(self, mock_context: Any) -> None:
        """Test that steps are numbered correctly."""
        steps_config = [{"capability_id": f"cap_{i}"} for i in range(5)]
        planner = SequentialPlanner(steps_config=steps_config)
        mock_context.config_update({"milestone_id": "m_001"})

        plan = await planner.plan(mock_context)

        for i, step in enumerate(plan.steps):
            assert step.step_id == f"m_001_step_{i + 1}"


# Make fixtures available
pytest_plugins = ["tests.unit.plan.conftest"]
