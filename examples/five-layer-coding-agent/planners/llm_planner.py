"""LLM-based planner that uses real model to generate plans."""
from __future__ import annotations

import json
from pathlib import Path

from dare_framework.context.kernel import IContext
from dare_framework.context import Message
from dare_framework.infra.component import ComponentType
from dare_framework.model import IModelAdapter, Prompt
from dare_framework.plan.types import ProposedPlan, ProposedStep


class LLMPlanner:
    """Planner that uses LLM to generate plans based on user tasks.

    This planner calls the actual model to understand the task and generate
    appropriate execution steps.
    """

    def __init__(self, model: IModelAdapter, workspace: Path, verbose: bool = True):
        """Initialize with a model adapter.

        Args:
            model: Model adapter for LLM calls.
            workspace: Workspace directory path.
            verbose: Whether to print verbose output.
        """
        self._model = model
        self._workspace = workspace
        self._verbose = verbose

    @property
    def component_type(self) -> ComponentType:
        """Component type for planner."""
        return ComponentType.PLANNER

    @property
    def name(self) -> str:
        return "llm-planner"

    async def plan(self, ctx: IContext) -> ProposedPlan:
        """Generate a plan using LLM.

        Args:
            ctx: Context containing task information.

        Returns:
            Generated plan.
        """
        # Get task description from context STM
        messages = ctx.stm_get()
        task_description = messages[-1].content if messages else "Unknown task"

        # Get available tools
        available_tools = self._get_available_tools()

        # Create prompt for LLM
        system_prompt = self._create_system_prompt(available_tools)
        user_prompt = f"""Task: {task_description}

Workspace: {self._workspace}

Please analyze this task and generate an execution plan using the available tools.
Output ONLY a valid JSON object with this structure:
{{
    "plan_description": "brief description of what the plan will do",
    "steps": [
        {{
            "step_id": "step1",
            "capability_id": "tool_name",
            "params": {{"param1": "value1"}},
            "description": "what this step does"
        }}
    ]
}}

Important:
- Use ONLY the tools listed in the available tools
- Provide concrete parameter values (actual paths, patterns, etc.)
- Keep the plan minimal but effective
- workspace path is: {self._workspace}
"""

        if self._verbose:
            print(f"\n💭 Asking LLM to plan for: {task_description[:50]}...")

        # Call model
        try:
            prompt = Prompt(messages=[
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt),
            ])

            response = await self._model.generate(prompt)
            response_text = response.content.strip()

            if self._verbose:
                print(f"📝 LLM response received ({len(response_text)} chars)")

        except Exception as e:
            if self._verbose:
                print(f"⚠️  LLM call failed: {type(e).__name__}: {str(e)[:100]}")
                print(f"⚙️  Using fallback plan...")

            return self._create_fallback_plan(task_description)

        # Parse response
        try:
            plan_data = self._parse_plan_response(response_text)
            steps = [
                ProposedStep(
                    step_id=step["step_id"],
                    capability_id=step["capability_id"],
                    params=step["params"],
                    description=step.get("description", ""),
                )
                for step in plan_data["steps"]
            ]

            plan = ProposedPlan(
                plan_description=plan_data["plan_description"],
                steps=steps,
            )

            if self._verbose:
                print(f"✓ Generated plan with {len(steps)} steps")

            return plan

        except Exception as e:
            if self._verbose:
                print(f"⚠️  Failed to parse LLM response, using fallback: {e}")

            # Fallback to simple plan
            return self._create_fallback_plan(task_description)

    def _create_system_prompt(self, available_tools: dict) -> str:
        """Create system prompt with available tools."""
        tools_desc = "\n".join([
            f"- {name}: {info['description']}\n  Parameters: {json.dumps(info['params'], indent=4)}"
            for name, info in available_tools.items()
        ])

        return f"""You are a coding task planner. Your job is to break down user tasks into executable steps using available tools.

Available Tools:
{tools_desc}

Guidelines:
1. Analyze the user's task carefully
2. Choose appropriate tools to accomplish the task
3. Provide concrete parameter values
4. Keep plans simple and focused
5. Output ONLY valid JSON, no explanations"""

    def _get_available_tools(self) -> dict:
        """Get available tools and their descriptions."""
        return {
            "read_file": {
                "description": "Read contents of a file",
                "params": {
                    "path": "absolute file path"
                }
            },
            "search_code": {
                "description": "Search for code patterns using regex",
                "params": {
                    "pattern": "search pattern (regex)",
                    "file_pattern": "file glob pattern (e.g., *.py)"
                }
            },
            "write_file": {
                "description": "Write content to a file",
                "params": {
                    "path": "absolute file path",
                    "content": "file content"
                }
            }
        }

    def _parse_plan_response(self, response: str) -> dict:
        """Parse LLM response to extract plan JSON."""
        # Try to find JSON in response
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.split("\n")
            # Remove first and last line (code block markers)
            response = "\n".join(lines[1:-1] if len(lines) > 2 else lines)

        # Try to parse as JSON
        return json.loads(response)

    def _create_fallback_plan(self, task_description: str) -> ProposedPlan:
        """Create a fallback plan when LLM parsing fails."""
        # Simple keyword-based fallback
        task_lower = task_description.lower()

        if "read" in task_lower or any(word in task_lower for word in ["什么", "介绍", "about"]):
            # Task is about reading/understanding the project
            return ProposedPlan(
                plan_description=f"Read project files to answer: {task_description}",
                steps=[
                    ProposedStep(
                        step_id="step1",
                        capability_id="read_file",
                        params={"path": str(self._workspace / "sample.py")},
                        description="Read main sample file",
                    ),
                ],
            )
        elif "todo" in task_lower:
            return ProposedPlan(
                plan_description="Search for TODO comments",
                steps=[
                    ProposedStep(
                        step_id="step1",
                        capability_id="search_code",
                        params={"pattern": "TODO", "file_pattern": "*.py"},
                        description="Search for TODO in Python files",
                    ),
                ],
            )
        elif "function" in task_lower or "def" in task_lower:
            return ProposedPlan(
                plan_description="Search for function definitions",
                steps=[
                    ProposedStep(
                        step_id="step1",
                        capability_id="search_code",
                        params={"pattern": r"^def\s+\w+", "file_pattern": "*.py"},
                        description="Search for function definitions",
                    ),
                ],
            )
        else:
            # Default: read main file
            return ProposedPlan(
                plan_description=f"Explore project to answer: {task_description}",
                steps=[
                    ProposedStep(
                        step_id="step1",
                        capability_id="read_file",
                        params={"path": str(self._workspace / "sample.py")},
                        description="Read sample file",
                    ),
                ],
            )
