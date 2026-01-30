"""Schema-based validator implementation.

This validator checks plans against tool schemas and security policies,
transforming untrusted ProposedPlan into trusted ValidatedPlan.
"""

from __future__ import annotations

from typing import Any, Literal

from dare_framework.context.kernel import IContext
from dare_framework.infra.component import ComponentType
from dare_framework.plan.interfaces import IValidator
from dare_framework.plan.types import (
    ProposedPlan,
    RunResult,
    ValidatedPlan,
    ValidatedStep,
    VerifyResult,
)
from dare_framework.security.types import RiskLevel, TrustedInput
from dare_framework.tool.kernel import IToolGateway


class SchemaValidator(IValidator):
    """Validates plans by checking against tool schemas and deriving trusted fields.

    This validator:
    1. Checks that all capability_ids exist in the ToolGateway registry
    2. Validates input params against tool input schemas
    3. Derives trusted security fields (risk_level) from registry, not from LLM
    4. Produces a ValidatedPlan with verified steps
    """

    def __init__(
        self,
        tool_gateway: IToolGateway,
        strict_schema_validation: bool = True,
        name: str = "schema_validator",
    ) -> None:
        """Initialize the schema validator.

        Args:
            tool_gateway: The tool gateway for capability lookups
            strict_schema_validation: Whether to fail on schema mismatch
            name: Component name for config lookups
        """
        self._tool_gateway = tool_gateway
        self._strict_schema_validation = strict_schema_validation
        self._name = name

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.VALIDATOR]:
        """Component category for config scoping."""
        return ComponentType.VALIDATOR

    async def validate_plan(self, plan: ProposedPlan, ctx: IContext) -> ValidatedPlan:
        """Validate a proposed plan and produce a validated plan.

        Args:
            plan: The proposed plan from the planner
            ctx: The execution context

        Returns:
            A validated plan with trusted fields derived from registry
        """
        errors: list[str] = []
        validated_steps: list[ValidatedStep] = []

        for step in plan.steps:
            # Check capability exists in registry
            capability = self._tool_gateway.get_capability(step.capability_id)

            if capability is None:
                errors.append(
                    f"Step {step.step_id}: Unknown capability '{step.capability_id}'"
                )
                continue

            # Validate params against input schema (if strict mode)
            if self._strict_schema_validation:
                schema_errors = self._validate_params_against_schema(
                    step.params, capability.input_schema
                )
                if schema_errors:
                    errors.extend(
                        [f"Step {step.step_id}: {e}" for e in schema_errors]
                    )
                    continue

            # Derive risk level from trusted registry metadata (NOT from LLM)
            risk_level = self._derive_risk_level(capability.metadata)

            # Create validated step with trusted fields
            validated_step = ValidatedStep(
                step_id=step.step_id,
                capability_id=step.capability_id,
                risk_level=risk_level,
                params=step.params,
                description=step.description,
                envelope=step.envelope,
            )
            validated_steps.append(validated_step)

        return ValidatedPlan(
            plan_description=plan.plan_description,
            steps=validated_steps,
            success=len(errors) == 0,
            errors=errors,
            metadata={
                "validator": "schema",
                "original_attempt": plan.attempt,
                "validated_step_count": len(validated_steps),
            },
        )

    async def verify_milestone(self, result: RunResult, ctx: IContext) -> VerifyResult:
        """Verify milestone completion based on execution result.

        Args:
            result: The run result from execution
            ctx: The execution context

        Returns:
            A verification result indicating success/failure
        """
        # Basic verification: success if RunResult.success and no errors
        success = result.success and not result.errors

        errors: list[str] = []
        if result.errors:
            errors.extend(result.errors)
        if not success:
            errors.append("Milestone verification failed: execution did not succeed")

        return VerifyResult(
            success=success,
            errors=errors,
            metadata={
                "verifier": "schema",
                "output_present": result.output is not None,
            },
        )

    def _validate_params_against_schema(
        self, params: dict[str, Any], schema: dict[str, Any]
    ) -> list[str]:
        """Validate params against JSON schema.

        Returns list of validation errors (empty if valid).
        """
        errors: list[str] = []

        # Basic required fields check
        required = schema.get("required", [])
        for field in required:
            if field not in params:
                errors.append(f"Missing required field: '{field}'")

        # Type checking for properties
        properties = schema.get("properties", {})
        for key, value in params.items():
            if key in properties:
                prop_schema = properties[key]
                type_error = self._check_type(key, value, prop_schema)
                if type_error:
                    errors.append(type_error)

        return errors

    def _check_type(
        self, key: str, value: Any, prop_schema: dict[str, Any]
    ) -> str | None:
        """Check if value matches the property schema type.

        Returns error message or None if valid.
        """
        expected_type = prop_schema.get("type")

        if expected_type is None:
            return None

        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        if expected_type in type_map:
            expected_python_type = type_map[expected_type]
            if not isinstance(value, expected_python_type):
                return f"Field '{key}': expected {expected_type}, got {type(value).__name__}"

        return None

    def _derive_risk_level(
        self, metadata: dict[str, Any] | None
    ) -> RiskLevel:
        """Derive risk level from trusted registry metadata.

        CRITICAL: This derives from registry metadata, NOT from LLM output.
        """
        if metadata is None:
            return RiskLevel.READ_ONLY

        risk_level_str = metadata.get("risk_level", "read_only")

        try:
            return RiskLevel(risk_level_str)
        except ValueError:
            # Default to read-only for unknown values
            return RiskLevel.READ_ONLY


class PermissiveValidator(IValidator):
    """A permissive validator that allows most plans (for testing only).

    WARNING: This validator is intended for testing and development only.
    It does not perform rigorous validation and trusts the planner output.
    """

    def __init__(
        self,
        default_risk_level: RiskLevel = RiskLevel.READ_ONLY,
        name: str = "permissive_validator",
    ) -> None:
        self._default_risk_level = default_risk_level
        self._name = name

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.VALIDATOR]:
        """Component category for config scoping."""
        return ComponentType.VALIDATOR

    async def validate_plan(self, plan: ProposedPlan, ctx: IContext) -> ValidatedPlan:
        """Validate plan permissively (minimal checks)."""
        validated_steps = [
            ValidatedStep(
                step_id=step.step_id,
                capability_id=step.capability_id,
                risk_level=self._default_risk_level,
                params=step.params,
                description=step.description,
                envelope=step.envelope,
            )
            for step in plan.steps
        ]

        return ValidatedPlan(
            plan_description=plan.plan_description,
            steps=validated_steps,
            success=True,
            errors=[],
            metadata={
                "validator": "permissive",
                "original_attempt": plan.attempt,
            },
        )

    async def verify_milestone(self, result: RunResult, ctx: IContext) -> VerifyResult:
        """Verify milestone permissively."""
        return VerifyResult(
            success=result.success,
            errors=result.errors if result.errors else [],
            metadata={"verifier": "permissive"},
        )


__all__ = ["PermissiveValidator", "SchemaValidator"]
