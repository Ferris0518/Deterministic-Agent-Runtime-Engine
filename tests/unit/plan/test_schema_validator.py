"""Tests for SchemaValidator and PermissiveValidator."""

from __future__ import annotations

import pytest

from dare_framework.infra.component import ComponentType
from dare_framework.plan._internal.schema_validator import (
    PermissiveValidator,
    SchemaValidator,
)
from dare_framework.plan.types import (
    ProposedPlan,
    ProposedStep,
    RunResult,
    ValidatedPlan,
)
from dare_framework.security.types import RiskLevel
from dare_framework.tool.types import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityMetadata,
    CapabilityType,
)


class TestSchemaValidator:
    """Tests for SchemaValidator."""

    async def test_name_and_component_type(self, mock_tool_gateway: Any) -> None:
        """Test that validator has correct name and component type."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)

        assert validator.name == "schema_validator"
        assert validator.component_type == ComponentType.VALIDATOR

    async def test_validate_plan_success(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test successful plan validation."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)
        plan = ProposedPlan(
            plan_description="Test plan",
            steps=[
                ProposedStep(
                    step_id="step_1",
                    capability_id="tool_read_file_001",
                    params={"path": "/test.txt"},
                    description="Read file",
                )
            ],
        )

        validated = await validator.validate_plan(plan, mock_context)

        assert validated.success is True
        assert len(validated.errors) == 0
        assert len(validated.steps) == 1
        assert validated.steps[0].capability_id == "tool_read_file_001"

    async def test_validate_plan_unknown_capability(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test validation failure for unknown capability."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)
        plan = ProposedPlan(
            plan_description="Test plan",
            steps=[
                ProposedStep(
                    step_id="step_1",
                    capability_id="unknown_capability",
                    params={},
                    description="Unknown step",
                )
            ],
        )

        validated = await validator.validate_plan(plan, mock_context)

        assert validated.success is False
        assert len(validated.errors) == 1
        assert "Unknown capability" in validated.errors[0]
        assert len(validated.steps) == 0

    async def test_validate_plan_derives_risk_level_from_registry(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test that risk level is derived from registry metadata."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)
        plan = ProposedPlan(
            plan_description="Test plan",
            steps=[
                ProposedStep(
                    step_id="step_1",
                    capability_id="tool_read_file_001",  # read_only in registry
                    params={},
                ),
                ProposedStep(
                    step_id="step_2",
                    capability_id="tool_write_file_001",  # idempotent_write in registry
                    params={},
                ),
            ],
        )

        validated = await validator.validate_plan(plan, mock_context)

        assert validated.success is True
        assert validated.steps[0].risk_level == RiskLevel.READ_ONLY
        assert validated.steps[1].risk_level == RiskLevel.IDEMPOTENT_WRITE

    async def test_validate_plan_missing_required_param(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test validation failure for missing required parameter."""
        validator = SchemaValidator(
            tool_gateway=mock_tool_gateway,
            strict_schema_validation=True,
        )
        plan = ProposedPlan(
            plan_description="Test plan",
            steps=[
                ProposedStep(
                    step_id="step_1",
                    capability_id="tool_read_file_001",
                    params={},  # Missing required "path"
                    description="Read without path",
                )
            ],
        )

        validated = await validator.validate_plan(plan, mock_context)

        assert validated.success is False
        assert any("Missing required" in e for e in validated.errors)

    async def test_validate_plan_multiple_steps_partial_failure(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test that validation stops at first failed step."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)
        plan = ProposedPlan(
            plan_description="Test plan",
            steps=[
                ProposedStep(
                    step_id="step_1",
                    capability_id="tool_read_file_001",
                    params={"path": "/test.txt"},
                ),
                ProposedStep(
                    step_id="step_2",
                    capability_id="unknown_capability",
                    params={},
                ),
                ProposedStep(
                    step_id="step_3",
                    capability_id="tool_write_file_001",
                    params={"path": "/out.txt", "content": "data"},
                ),
            ],
        )

        validated = await validator.validate_plan(plan, mock_context)

        # First step succeeds, second fails, third is not processed
        assert validated.success is False
        assert len(validated.steps) == 1  # Only first step validated

    async def test_validate_plan_preserves_step_metadata(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test that validation preserves step metadata."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)
        plan = ProposedPlan(
            plan_description="Test plan",
            steps=[
                ProposedStep(
                    step_id="custom_step_id",
                    capability_id="tool_read_file_001",
                    params={"path": "/test.txt"},
                    description="Custom description",
                )
            ],
        )

        validated = await validator.validate_plan(plan, mock_context)

        assert validated.steps[0].step_id == "custom_step_id"
        assert validated.steps[0].description == "Custom description"
        assert validated.steps[0].params == {"path": "/test.txt"}

    async def test_verify_milestone_success(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test milestone verification success."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)
        result = RunResult(success=True, output="completed", errors=[])

        verify_result = await validator.verify_milestone(result, mock_context)

        assert verify_result.success is True
        assert len(verify_result.errors) == 0

    async def test_verify_milestone_failure(self, mock_tool_gateway: Any, mock_context: Any) -> None:
        """Test milestone verification failure."""
        validator = SchemaValidator(tool_gateway=mock_tool_gateway)
        result = RunResult(success=False, output=None, errors=["Execution failed"])

        verify_result = await validator.verify_milestone(result, mock_context)

        assert verify_result.success is False
        assert "Execution failed" in verify_result.errors

    async def test_custom_name(self, mock_tool_gateway: Any) -> None:
        """Test that custom name is respected."""
        validator = SchemaValidator(
            tool_gateway=mock_tool_gateway,
            name="custom_validator",
        )

        assert validator.name == "custom_validator"


class TestPermissiveValidator:
    """Tests for PermissiveValidator."""

    async def test_name_and_component_type(self) -> None:
        """Test that validator has correct name and component type."""
        validator = PermissiveValidator()

        assert validator.name == "permissive_validator"
        assert validator.component_type == ComponentType.VALIDATOR

    async def test_always_succeeds(self, mock_context: Any) -> None:
        """Test that permissive validator always succeeds."""
        validator = PermissiveValidator()
        plan = ProposedPlan(
            plan_description="Any plan",
            steps=[
                ProposedStep(
                    step_id="step_1",
                    capability_id="any_capability",  # Unknown capability
                    params={},
                )
            ],
        )

        validated = await validator.validate_plan(plan, mock_context)

        assert validated.success is True
        assert len(validated.errors) == 0

    async def test_uses_default_risk_level(self, mock_context: Any) -> None:
        """Test that default risk level is used."""
        validator = PermissiveValidator(default_risk_level=RiskLevel.COMPENSATABLE)
        plan = ProposedPlan(
            plan_description="Test",
            steps=[ProposedStep(step_id="s1", capability_id="cap1", params={})],
        )

        validated = await validator.validate_plan(plan, mock_context)

        assert validated.steps[0].risk_level == RiskLevel.COMPENSATABLE

    async def test_verify_milestone_passes_through(self, mock_context: Any) -> None:
        """Test that milestone verification passes through result."""
        validator = PermissiveValidator()
        result = RunResult(success=True, output="done")

        verify_result = await validator.verify_milestone(result, mock_context)

        assert verify_result.success is True


# Import fixtures
pytest_plugins = ["tests.unit.plan.conftest"]
