"""LLM-based planner implementation using model adapters.

This planner uses an IModelAdapter to generate plans via LLM calls,
parsing the response into ProposedPlan structures.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from dare_framework.context.kernel import IContext
from dare_framework.context.types import AssembledContext, Message
from dare_framework.infra.component import ComponentType
from dare_framework.model.kernel import IModelAdapter
from dare_framework.model.types import GenerateOptions, ModelInput, ModelResponse
from dare_framework.plan.interfaces import IPlanner
from dare_framework.plan.types import ProposedPlan, ProposedStep


DEFAULT_PLANNING_PROMPT = """You are a planning agent. Given a task description and available tools,
break down the task into a sequence of steps. Each step should use one of the available tools.

Respond with a JSON object in this exact format:
{
    "plan_description": "Brief description of the overall plan",
    "steps": [
        {
            "capability_id": "tool_xxx",
            "params": {"key": "value"},
            "description": "What this step does"
        }
    ]
}

Rules:
- Use only the provided capability_ids
- Params must match the tool's input schema
- Steps should be ordered logically
- Keep descriptions concise but clear"""


class LLMPlanner(IPlanner):
    """LLM-based planner that generates plans using a model adapter.

    This planner:
    1. Assembles a planning prompt with available tools from context
    2. Calls the model adapter to generate a plan
    3. Parses the response into a ProposedPlan
    """

    def __init__(
        self,
        model_adapter: IModelAdapter,
        system_prompt: str | None = None,
        name: str = "llm_planner",
        temperature: float = 0.1,
        max_tokens: int | None = None,
    ) -> None:
        """Initialize the LLM planner.

        Args:
            model_adapter: The model adapter to use for generation
            system_prompt: Custom system prompt (uses default if None)
            name: Component name for config lookups
            temperature: Generation temperature (default 0.1 for deterministic plans)
            max_tokens: Max tokens for generation
        """
        self._model = model_adapter
        self._system_prompt = system_prompt or DEFAULT_PLANNING_PROMPT
        self._name = name
        self._temperature = temperature
        self._max_tokens = max_tokens

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.PLANNER]:
        """Component category for config scoping."""
        return ComponentType.PLANNER

    async def plan(self, ctx: IContext) -> ProposedPlan:
        """Generate a plan using LLM.

        Args:
            ctx: The context containing task info and available tools

        Returns:
            A ProposedPlan parsed from the LLM response
        """
        # Get task info from context
        metadata = ctx.config or {}
        task_desc = metadata.get("task_description", "Execute task")
        milestone_desc = metadata.get("milestone_description", task_desc)
        milestone_id = metadata.get("milestone_id", "milestone_001")
        attempt = metadata.get("plan_attempt", 0)

        # Get available tools from context
        toollist = ctx.listing_tools()

        # Build the planning prompt
        messages = [
            Message(role="system", content=self._system_prompt),
            Message(
                role="user",
                content=self._build_planning_prompt(milestone_desc, toollist),
            ),
        ]

        # Create model input
        model_input = ModelInput(
            messages=messages,
            tools=[],  # Planning doesn't use tools, it produces the plan
            metadata={
                "purpose": "planning",
                "milestone_id": milestone_id,
                "attempt": attempt,
            },
        )

        # Call model
        options = GenerateOptions(
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        response = await self._model.generate(model_input, options=options)

        # Parse response into ProposedPlan
        return self._parse_plan_response(
            response, milestone_id, attempt, milestone_desc
        )

    def _build_planning_prompt(
        self, task_description: str, toollist: list[dict[str, Any]]
    ) -> str:
        """Build the planning prompt with task and available tools."""
        # Extract capability info from tool definitions
        capabilities_info = []
        for tool_def in toollist:
            func = tool_def.get("function", {})
            cap_id = tool_def.get("capability_id", "unknown")
            name = func.get("name", cap_id)
            desc = func.get("description", "No description")
            params = func.get("parameters", {})
            capabilities_info.append(
                f"- {cap_id} ({name}): {desc}\n  Parameters: {json.dumps(params, indent=2)}"
            )

        tools_section = (
            "\n".join(capabilities_info)
            if capabilities_info
            else "No tools available"
        )

        return f"""Task: {task_description}

Available Tools:
{tools_section}

Generate a plan to complete this task using the available tools."""

    def _parse_plan_response(
        self,
        response: ModelResponse,
        milestone_id: str,
        attempt: int,
        task_description: str,
    ) -> ProposedPlan:
        """Parse model response into ProposedPlan."""
        content = response.content or "{}"

        # Try to extract JSON from the response
        try:
            # First, try direct JSON parse
            plan_data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            plan_data = self._extract_json_from_markdown(content)

        if not isinstance(plan_data, dict):
            plan_data = {}

        # Build steps
        steps: list[ProposedStep] = []
        step_list = plan_data.get("steps", [])

        if not isinstance(step_list, list):
            step_list = []

        for i, step_data in enumerate(step_list):
            if not isinstance(step_data, dict):
                continue

            step = ProposedStep(
                step_id=f"{milestone_id}_step_{i + 1}",
                capability_id=step_data.get("capability_id", "noop"),
                params=step_data.get("params", {}),
                description=step_data.get("description", f"Step {i + 1}"),
            )
            steps.append(step)

        # If no steps parsed, create a fallback step
        if not steps:
            steps.append(
                ProposedStep(
                    step_id=f"{milestone_id}_step_1",
                    capability_id="noop",
                    params={"original_task": task_description},
                    description=f"Fallback: {task_description}",
                )
            )

        return ProposedPlan(
            plan_description=plan_data.get(
                "plan_description", f"Plan for: {task_description}"
            ),
            steps=steps,
            attempt=attempt,
            metadata={
                "planner": "llm",
                "milestone_id": milestone_id,
                "model_response": content,
            },
        )

    def _extract_json_from_markdown(self, content: str) -> dict[str, Any]:
        """Extract JSON from markdown code blocks."""
        import re

        # Look for JSON in code blocks
        patterns = [
            r"```json\s*(.*?)\s*```",  # ```json ... ```
            r"```\s*(.*?)\s*```",  # ``` ... ```
            r"\{.*\}",  # Any JSON-like structure
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        return {}


__all__ = ["LLMPlanner", "DEFAULT_PLANNING_PROMPT"]
