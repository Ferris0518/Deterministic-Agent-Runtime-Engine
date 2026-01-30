"""Tests for LLMRemediator and SimpleRemediator."""

from __future__ import annotations

import json

import pytest

from dare_framework.infra.component import ComponentType
from dare_framework.plan._internal.llm_remediator import (
    DEFAULT_REMEDIATION_PROMPT,
    LLMRemediator,
    NoOpRemediator,
    SimpleRemediator,
)
from dare_framework.plan.types import VerifyResult


class TestLLMRemediator:
    """Tests for LLMRemediator."""

    async def test_name_and_component_type(self) -> None:
        """Test that remediator has correct name and component type."""
        mock_model = MockModelAdapter()
        remediator = LLMRemediator(model_adapter=mock_model)

        assert remediator.name == "llm_remediator"
        assert remediator.component_type == ComponentType.REMEDIATOR

    async def test_remediation_generation(self, mock_context: Any) -> None:
        """Test basic remediation generation."""
        response_json = json.dumps({
            "reflection": "The file path was invalid.",
            "suggestions": ["Check file exists", "Use absolute path"]
        })
        mock_model = MockModelAdapter(responses=[response_json])
        remediator = LLMRemediator(model_adapter=mock_model)

        verify_result = VerifyResult(
            success=False,
            errors=["File not found: /invalid/path"],
        )

        reflection = await remediator.remediate(verify_result, mock_context)

        assert "The file path was invalid" in reflection
        assert "Check file exists" in reflection
        assert "Use absolute path" in reflection

    async def test_model_input_contains_errors(self, mock_context: Any) -> None:
        """Test that model input includes error details."""
        mock_model = MockModelAdapter(responses=['{"reflection": "Test"}'])
        remediator = LLMRemediator(model_adapter=mock_model)

        verify_result = VerifyResult(
            success=False,
            errors=["Error 1", "Error 2"],
        )

        await remediator.remediate(verify_result, mock_context)

        user_message = next(
            m for m in mock_model.inputs[0].messages if m.role == "user"
        )
        assert "Error 1" in user_message.content
        assert "Error 2" in user_message.content

    async def test_default_system_prompt(self, mock_context: Any) -> None:
        """Test that default system prompt is used."""
        mock_model = MockModelAdapter(responses=['{"reflection": "Test"}'])
        remediator = LLMRemediator(model_adapter=mock_model)

        await remediator.remediate(VerifyResult(success=False), mock_context)

        system_message = next(
            m for m in mock_model.inputs[0].messages if m.role == "system"
        )
        assert DEFAULT_REMEDIATION_PROMPT in system_message.content

    async def test_parse_json_from_markdown(self, mock_context: Any) -> None:
        """Test parsing JSON from markdown code block."""
        markdown_response = '''```json
{
    "reflection": "Markdown JSON",
    "suggestions": ["Suggestion 1"]
}
```'''
        mock_model = MockModelAdapter(responses=[markdown_response])
        remediator = LLMRemediator(model_adapter=mock_model)

        reflection = await remediator.remediate(VerifyResult(success=False), mock_context)

        assert "Markdown JSON" in reflection
        assert "Suggestion 1" in reflection

    async def test_fallback_on_parse_failure(self, mock_context: Any) -> None:
        """Test fallback when JSON parsing fails."""
        raw_response = "Raw text response without JSON"
        mock_model = MockModelAdapter(responses=[raw_response])
        remediator = LLMRemediator(model_adapter=mock_model)

        reflection = await remediator.remediate(VerifyResult(success=False), mock_context)

        # Should return the raw content
        assert reflection == raw_response

    async def test_custom_name(self) -> None:
        """Test that custom name is respected."""
        mock_model = MockModelAdapter()
        remediator = LLMRemediator(model_adapter=mock_model, name="custom_remediator")

        assert remediator.name == "custom_remediator"


class TestSimpleRemediator:
    """Tests for SimpleRemediator."""

    async def test_name_and_component_type(self) -> None:
        """Test that remediator has correct name and component type."""
        remediator = SimpleRemediator()

        assert remediator.name == "simple_remediator"
        assert remediator.component_type == ComponentType.REMEDIATOR

    async def test_unknown_capability_guidance(self, mock_context: Any) -> None:
        """Test guidance for unknown capability error."""
        remediator = SimpleRemediator()
        verify_result = VerifyResult(
            success=False,
            errors=["Unknown capability 'fake_tool'"],
        )

        reflection = await remediator.remediate(verify_result, mock_context)

        assert "doesn't exist in the registry" in reflection

    async def test_missing_required_guidance(self, mock_context: Any) -> None:
        """Test guidance for missing required parameter."""
        remediator = SimpleRemediator()
        verify_result = VerifyResult(
            success=False,
            errors=["Missing required field: 'path'"],
        )

        reflection = await remediator.remediate(verify_result, mock_context)

        assert "required parameter was missing" in reflection

    async def test_schema_error_guidance(self, mock_context: Any) -> None:
        """Test guidance for schema/type error."""
        remediator = SimpleRemediator()
        verify_result = VerifyResult(
            success=False,
            errors=["Parameter type mismatch: expected string, got number"],
        )

        reflection = await remediator.remediate(verify_result, mock_context)

        assert "type mismatch" in reflection.lower()

    async def test_permission_error_guidance(self, mock_context: Any) -> None:
        """Test guidance for permission error."""
        remediator = SimpleRemediator()
        verify_result = VerifyResult(
            success=False,
            errors=["Operation not allowed: permission denied"],
        )

        reflection = await remediator.remediate(verify_result, mock_context)

        assert "not permitted" in reflection

    async def test_timeout_error_guidance(self, mock_context: Any) -> None:
        """Test guidance for timeout error."""
        remediator = SimpleRemediator()
        verify_result = VerifyResult(
            success=False,
            errors=["Operation timed out after 30s"],
        )

        reflection = await remediator.remediate(verify_result, mock_context)

        assert "timed out" in reflection

    async def test_multiple_errors(self, mock_context: Any) -> None:
        """Test guidance for multiple errors."""
        remediator = SimpleRemediator()
        verify_result = VerifyResult(
            success=False,
            errors=[
                "Unknown capability 'tool_a'",
                "Unknown capability 'tool_b'",
            ],
        )

        reflection = await remediator.remediate(verify_result, mock_context)

        # Should include both errors
        assert "tool_a" in reflection or "doesn't exist" in reflection

    async def test_no_errors(self, mock_context: Any) -> None:
        """Test guidance when no specific errors provided."""
        remediator = SimpleRemediator()
        verify_result = VerifyResult(success=False, errors=[])

        reflection = await remediator.remediate(verify_result, mock_context)

        assert "without specific errors" in reflection


class TestNoOpRemediator:
    """Tests for NoOpRemediator."""

    async def test_name_and_component_type(self) -> None:
        """Test that remediator has correct name and component type."""
        remediator = NoOpRemediator()

        assert remediator.name == "noop_remediator"
        assert remediator.component_type == ComponentType.REMEDIATOR

    async def test_returns_empty_string(self, mock_context: Any) -> None:
        """Test that remediator returns empty string."""
        remediator = NoOpRemediator()
        verify_result = VerifyResult(success=False, errors=["Some error"])

        reflection = await remediator.remediate(verify_result, mock_context)

        assert reflection == ""


# Import fixtures
from tests.unit.plan.conftest import MockModelAdapter

pytest_plugins = ["tests.unit.plan.conftest"]
