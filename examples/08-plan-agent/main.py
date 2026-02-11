"""Example 08: Plan Agent (plan_v2.Planner mounted on ReactAgent).

Run a Plan Agent that has only plan tools (create_plan, validate_plan, decompose_task, etc.).
After the model responds, we print PlannerState and copy_for_execution() so you can verify
the planner effect. No execution tools — planning only.

Usage:
  Set OPENROUTER_API_KEY, then:
  python main.py
  python main.py "Your custom task description"
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dare_framework.agent import BaseAgent
from dare_framework.config import Config
from dare_framework.model import OpenRouterModelAdapter
from dare_framework.model.types import Prompt
from dare_framework.plan_v2 import Planner, PlannerState


async def main() -> None:
    api_key = os.getenv("OPENROUTER_API_KEY","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")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set")
        sys.exit(1)

    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
    max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))

    task_description = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Plan how to implement a small Python script that reads a config file and prints its contents. "
        "Give a short plan_description and 3–5 steps (step_id, description, optional params)."
    )

    workspace = Path(__file__).parent / "workspace"
    workspace.mkdir(exist_ok=True)

    # Planner state: identity for handoff; Plan Agent will fill plan_description + steps
    state = PlannerState(
        task_id="example-08-task-1",
        session_id="example-08-session-1",
    )
    planner = Planner(state)

    model = OpenRouterModelAdapter(
        model=model_name,
        api_key=api_key,
        extra={"max_tokens": max_tokens},
    )
    config = Config(workspace_dir=str(workspace), user_dir=str(Path.home()))

    plan_sys_prompt = Prompt(
        prompt_id="plan-agent.system",
        role="system",
        content="""You are a planning-only agent. You have tools to create and validate a plan.
When the user gives a task:
1. Call create_plan with plan_description (short summary) and steps: a list of objects, each with step_id (e.g. "step1"), description (what to do), and optional params (dict).
2. Then call validate_plan(success=True) to confirm the plan.
Do not execute any steps yourself; only produce the plan. Keep steps concise and ordered.""",
        supported_models=[],
        order=0,
    )

    # Plan Agent: ReactAgent + plan_provider only (no file/shell tools)
    builder = (
        BaseAgent.react_agent_builder("plan-agent")
        .with_model(model)
        .with_config(config)
        .with_prompt(plan_sys_prompt)
        .with_plan_provider(planner)
    )
    agent = await builder.build()

    print("Plan Agent (plan_v2) — planning only, no execution tools")
    print(f"Model: {model_name}")
    print(f"Task: {task_description}")
    print("-" * 60)

    result = await agent.run(task_description)
    content = (result.output or result.output_text or "") if hasattr(result, "output") else str(result)
    print("Agent final output:")
    print(content)
    print("-" * 60)

    # Verify planner state
    pp = getattr(agent, "plan_provider", None)
    if pp is None:
        print("No plan_provider on agent (builder did not mount planner?).")
        return
    plan_state = getattr(pp, "state", None)
    if plan_state is None:
        print("plan_provider has no .state")
        return

    print("PlannerState after run:")
    print(f"  task_id: {plan_state.task_id}")
    print(f"  session_id: {plan_state.session_id}")
    print(f"  plan_description: {plan_state.plan_description or '(empty)'}")
    print(f"  steps: {len(plan_state.steps)}")
    for i, s in enumerate(plan_state.steps):
        print(f"    [{i+1}] {s.step_id}: {s.description}")
    print(f"  plan_success: {plan_state.plan_success}")
    print(f"  plan_errors: {plan_state.plan_errors}")

    handoff = plan_state.copy_for_execution()
    print("\ncopy_for_execution() (for Execution Agent):")
    print(f"  task_id: {handoff.task_id}, session_id: {handoff.session_id}")
    print(f"  steps count: {len(handoff.steps)}")
    print("  (plan_errors / last_verify_errors stripped in handoff)")


if __name__ == "__main__":
    asyncio.run(main())
