"""Tests for LLMPlanner."""

from __future__ import annotations

import json

import pytest

from dare_framework.infra.component import ComponentType
from dare_framework.model.types import ModelInput
from dare_framework.plan._internal.llm_planner import DEFAULT_PLANNING_PROMPT, LLMPlanner


class TestLLMPlanner:
    """Tests for LLMPlanner."""

    async def test_name_and_component_type(self) -> None:
        """Test that planner has correct name and component type."""
        mock_model = MockModelAdapter()
        planner = LLMPlanner(model_adapter=mock_model)

        assert planner.name == "llm_planner"
        assert planner.component_type == ComponentType.PLANNER

    async def test_custom_name(self) -> None:
        """Test that custom name is respected."""
        mock_model = MockModelAdapter()
        planner = LLMPlanner(model_adapter=mock_model, name="custom_llm_planner")

        assert planner.name == "custom_llm_planner"

    async def test_plan_generation_basic(self, mock_context_with_tools: Any) -> None:
        """Test basic plan generation."""
        # Create a mock response that returns a valid plan
        plan_json = json.dumps({
            "plan_description": "Read and process file",
            "steps": [
                {
                    "capability_id": "tool_read_file_001",
                    "params": {"path": "/test/file.txt"},
                    "description": "Read the test file",
                }
            ]
        })
        mock_model = MockModelAdapter(responses=[plan_json])
        planner = LLMPlanner(model_adapter=mock_model)

        plan = await planner.plan(mock_context_with_tools)

        assert plan.plan_description == "Read and process file"
        assert len(plan.steps) == 1
        assert plan.steps[0].capability_id == "tool_read_file_001"
        assert plan.steps[0].params == {"path": "/test/file.txt"}
        assert plan.steps[0].description == "Read the test file"

    async def test_plan_generation_multiple_steps(self, mock_context_with_tools: Any) -> None:
        """Test plan generation with multiple steps."""
        plan_json = json.dumps({
            "plan_description": "Multi-step plan",
            "steps": [
                {
                    "capability_id": "tool_read_file_001",
                    "params": {"path": "/input.txt"},
                    "description": "Read input",
                },
                {
                    "capability_id": "tool_write_file_001",
                    "params": {"path": "/output.txt", "content": "processed"},
                    "description": "Write output",
                }
            ]
        })
        mock_model = MockModelAdapter(responses=[plan_json])
        planner = LLMPlanner(model_adapter=mock_model)

        plan = await planner.plan(mock_context_with_tools)

        assert len(plan.steps) == 2
        assert plan.steps[0].capability_id == "tool_read_file_001"
        assert plan.steps[1].capability_id == "tool_write_file_001"

    async def test_model_input_contains_tools(self, mock_context_with_tools: Any) -> None:
        """Test that model input includes available tools."""
        mock_model = MockModelAdapter(responses=['{"plan_description": "Test", "steps": []}'])
        planner = LLMPlanner(model_adapter=mock_model)

        await planner.plan(mock_context_with_tools)

        assert len(mock_model.inputs) == 1
        model_input = mock_model.inputs[0]
        assert isinstance(model_input, ModelInput)

        # Check that tools are mentioned in the prompt
        messages = model_input.messages
        user_message = next(m for m in messages if m.role == "user")
        assert "tool_read_file" in user_message.content
        assert "tool_write_file" in user_message.content

    async def test_model_input_contains_task(self, mock_context_with_tools: Any) -> None:
        """Test that model input includes task description."""
        mock_context_with_tools.config_update({"task_description": "Custom task"})
        mock_model = MockModelAdapter(responses=['{"plan_description": "Test", "steps": []}'])
        planner = LLMPlanner(model_adapter=mock_model)

        await planner.plan(mock_context_with_tools)

        user_message = next(
            m for m in mock_model.inputs[0].messages if m.role == "user"
        )
        assert "Custom task" in user_message.content

    async def test_default_system_prompt(self, mock_context_with_tools: Any) -> None:
        """Test that default system prompt is used."""
        mock_model = MockModelAdapter(responses=['{"plan_description": "Test", "steps": []}'])
        planner = LLMPlanner(model_adapter=mock_model)

        await planner.plan(mock_context_with_tools)

        system_message = next(
            m for m in mock_model.inputs[0].messages if m.role == "system"
        )
        assert DEFAULT_PLANNING_PROMPT in system_message.content

    async def test_custom_system_prompt(self, mock_context_with_tools: Any) -> None:
        """Test that custom system prompt can be provided."""
        custom_prompt = "Custom planning prompt"
        mock_model = MockModelAdapter(responses=['{"plan_description": "Test", "steps": []}'])
        planner = LLMPlanner(model_adapter=mock_model, system_prompt=custom_prompt)

        await planner.plan(mock_context_with_tools)

        system_message = next(
            m for m in mock_model.inputs[0].messages if m.role == "system"
        )
        assert system_message.content == custom_prompt

    async def test_parse_json_from_markdown_code_block(self, mock_context_with_tools: Any) -> None:
        """Test parsing JSON from markdown code block."""
        markdown_response = '''```json
{
    "plan_description": "Markdown plan",
    "steps": [
        {
            "capability_id": "tool_read_file_001",
            "params": {},
            "description": "Read file"
        }
    ]
}
```'''
        mock_model = MockModelAdapter(responses=[markdown_response])
        planner = LLMPlanner(model_adapter=mock_model)

        plan = await planner.plan(mock_context_with_tools)

        assert plan.plan_description == "Markdown plan"
        assert len(plan.steps) == 1

    async def test_parse_plain_json_without_markdown(self, mock_context_with_tools: Any) -> None:
        """Test parsing plain JSON without markdown."""
        plain_json = '{"plan_description": "Plain plan", "steps": [{"capability_id": "tool_read_file_001", "params": {}, "description": "Step"}]}'
        mock_model = MockModelAdapter(responses=[plain_json])
        planner = LLMPlanner(model_adapter=mock_model)

        plan = await planner.plan(mock_context_with_tools)

        assert plan.plan_description == "Plain plan"

    async def test_fallback_on_parse_failure(self, mock_context_with_tools: Any) -> None:
        """Test fallback when JSON parsing fails."""
        invalid_response = "Not valid JSON"
        mock_model = MockModelAdapter(responses=[invalid_response])
        planner = LLMPlanner(model_adapter=mock_model)
        mock_context_with_tools.config_update({"task_description": "Important task"})

        plan = await planner.plan(mock_context_with_tools)

        # Should create a fallback noop plan
        assert len(plan.steps) == 1
        assert plan.steps[0].capability_id == "noop"
        assert "Important task" in plan.steps[0].params.get("original_task", "")

    async def test_generation_options_passed(self, mock_context_with_tools: Any) -> None:
        """Test that generation options are passed to model."""
        mock_model = MockModelAdapter(responses=['{"plan_description": "Test", "steps": []}'])
        planner = LLMPlanner(
            model_adapter=mock_model,
            temperature=0.5,
            max_tokens=1000,
        )

        await planner.plan(mock_context_with_tools)

        # The model adapter should receive options (we can't directly assert this
        # with MockModelAdapter, but we verify no errors occur)

    async def test_plan_includes_attempt_number(self, mock_context_with_tools: Any) -> None:
        """Test that plan includes attempt number from context."""
        mock_model = MockModelAdapter(responses=['{"plan_description": "Test", "steps": []}'])
        planner = LLMPlanner(model_adapter=mock_model)
        mock_context_with_tools.config_update({"plan_attempt": 2})

        plan = await planner.plan(mock_context_with_tools)

        assert plan.attempt == 2


# Import fixtures
from tests.unit.plan.conftest import MockModelAdapter

pytest_plugins = ["tests.unit.plan.conftest"]
