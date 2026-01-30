"""Mock Plan Example - Demonstrates Plan Loop with deterministic planners.

This example shows how to use the Plan Loop with mock/deterministic planners
and validators, without requiring any external LLM API calls.

Run:
  PYTHONPATH=. python examples/plan/mock_plan_example.py

Key concepts demonstrated:
1. SimplePlanner - deterministic single-step plan generation
2. SequentialPlanner - multi-step workflow plans
3. SchemaValidator - validating plans against tool schemas
4. PlanLoop - orchestrating plan generation with retry logic
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dare_framework.context.kernel import IContext, IRetrievalContext
from dare_framework.context.types import AssembledContext, Budget, Message
from dare_framework.infra.component import ComponentType
from dare_framework.plan import (
    Milestone,
    PlanLoop,
    PlanLoopConfig,
    SchemaValidator,
    SequentialPlanner,
    SimplePlanner,
    ValidatedPlan,
)
from dare_framework.plan.types import Task
from dare_framework.security.types import RiskLevel
from dare_framework.tool.kernel import IToolGateway
from dare_framework.tool.types import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityMetadata,
    CapabilityType,
)


class MockContext(IContext):
    """Mock context for demonstration."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._messages: list[Message] = []
        self.id = "mock_ctx_001"
        self.budget = Budget(max_tool_calls=10)
        self.short_term_memory = MockRetrievalContext()
        self.long_term_memory = None
        self.knowledge = None
        self.toollist: list[dict[str, Any]] = []

    def stm_add(self, message: Message) -> None:
        self._messages.append(message)

    def stm_get(self) -> list[Message]:
        return list(self._messages)

    def stm_clear(self) -> list[Message]:
        old = list(self._messages)
        self._messages.clear()
        return old

    def budget_use(self, resource: str, amount: float) -> None:
        print(f"  [Budget] Using {amount} {resource}")

    def budget_check(self) -> None:
        pass

    def budget_remaining(self, resource: str) -> float:
        return 100.0

    def listing_tools(self) -> list[dict[str, Any]]:
        return self.toollist

    def assemble(self, **options: Any) -> AssembledContext:
        return AssembledContext(
            messages=self._messages,
            tools=self.toollist,
            metadata={"stage": options.get("stage", "unknown")},
        )

    def config_update(self, patch: dict[str, Any]) -> None:
        self._config.update(patch)
        if "plan_attempt" in patch:
            print(f"  [Context] Plan attempt: {patch['plan_attempt']}")

    @property
    def config(self) -> dict[str, Any]:
        return self._config


class MockRetrievalContext(IRetrievalContext):
    """Mock retrieval context."""

    def get(self, query: str = "", **kwargs: Any) -> list[Message]:
        return []


class MockToolGateway(IToolGateway):
    """Mock tool gateway with sample capabilities."""

    def __init__(self) -> None:
        self._capabilities: dict[str, CapabilityDescriptor] = {
            "cap_read": CapabilityDescriptor(
                id="cap_read",
                type=CapabilityType.TOOL,
                name="read_file",
                description="Read file contents",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
                metadata=CapabilityMetadata(
                    risk_level="read_only",
                    capability_kind=CapabilityKind.TOOL,
                ),
            ),
            "cap_write": CapabilityDescriptor(
                id="cap_write",
                type=CapabilityType.TOOL,
                name="write_file",
                description="Write file contents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
                metadata=CapabilityMetadata(
                    risk_level="idempotent_write",
                    capability_kind=CapabilityKind.TOOL,
                ),
            ),
            "cap_search": CapabilityDescriptor(
                id="cap_search",
                type=CapabilityType.TOOL,
                name="search_code",
                description="Search code in workspace",
                input_schema={
                    "type": "object",
                    "properties": {"pattern": {"type": "string"}},
                    "required": ["pattern"],
                },
                metadata=CapabilityMetadata(
                    risk_level="read_only",
                    capability_kind=CapabilityKind.TOOL,
                ),
            ),
        }

    async def list_capabilities(self) -> list[CapabilityDescriptor]:
        return list(self._capabilities.values())

    async def invoke(self, capability_id: str, params: dict[str, Any], *, envelope: Any) -> Any:
        print(f"  [Tool] Invoking {capability_id} with {params}")
        return {"success": True}

    def register_provider(self, provider: object) -> None:
        pass

    def get_capability(self, capability_id: str, *, include_disabled: bool = False) -> CapabilityDescriptor | None:
        return self._capabilities.get(capability_id)


async def demo_simple_planner() -> None:
    """Demonstrate SimplePlanner with PlanLoop."""
    print("\n" + "=" * 60)
    print("Demo 1: SimplePlanner - Single Step Plan")
    print("=" * 60)

    # Create components
    planner = SimplePlanner(default_capability_id="cap_read")
    tool_gateway = MockToolGateway()
    validator = SchemaValidator(tool_gateway=tool_gateway)

    loop = PlanLoop(
        planner=planner,
        validator=validator,
        config=PlanLoopConfig(max_attempts=2),
    )

    # Create context and milestone
    ctx = MockContext(config={"task_description": "Read the config file"})
    milestone = Milestone(
        milestone_id="ms_001",
        description="Read config file",
        user_input="Read the configuration from /etc/config.json",
    )

    # Run plan loop
    print(f"\nGenerating plan for: {milestone.user_input}")
    result = await loop.run(milestone, ctx)

    # Display results
    if result.success:
        plan = result.validated_plan
        print(f"\n✅ Plan generated successfully!")
        print(f"   Description: {plan.plan_description}")
        print(f"   Steps: {len(plan.steps)}")
        for i, step in enumerate(plan.steps, 1):
            print(f"     {i}. [{step.risk_level.value}] {step.capability_id}")
            print(f"        Params: {step.params}")
    else:
        print(f"\n❌ Plan generation failed after {len(result.attempts)} attempts")
        for attempt in result.attempts:
            print(f"   Attempt {attempt.attempt_number}: {attempt.validation_errors}")


async def demo_sequential_planner() -> None:
    """Demonstrate SequentialPlanner with PlanLoop."""
    print("\n" + "=" * 60)
    print("Demo 2: SequentialPlanner - Multi-Step Workflow")
    print("=" * 60)

    # Define a workflow with multiple steps
    workflow_steps = [
        {
            "capability_id": "cap_search",
            "params": {"pattern": "TODO"},
            "description": "Find TODO comments in code",
        },
        {
            "capability_id": "cap_read",
            "params": {"path": "/path/to/todo/file"},
            "description": "Read the file containing TODOs",
        },
        {
            "capability_id": "cap_write",
            "params": {"path": "/path/to/report.txt", "content": "TODO Report"},
            "description": "Write TODO report",
        },
    ]

    planner = SequentialPlanner(steps_config=workflow_steps)
    tool_gateway = MockToolGateway()
    validator = SchemaValidator(tool_gateway=tool_gateway)

    loop = PlanLoop(
        planner=planner,
        validator=validator,
        config=PlanLoopConfig(max_attempts=2),
    )

    ctx = MockContext(config={"task_description": "Generate TODO report"})
    milestone = Milestone(
        milestone_id="ms_002",
        description="Generate TODO report",
        user_input="Find all TODOs, read the files, and generate a report",
    )

    print(f"\nGenerating multi-step plan for: {milestone.user_input}")
    result = await loop.run(milestone, ctx)

    if result.success:
        plan = result.validated_plan
        print(f"\n✅ Multi-step plan generated successfully!")
        print(f"   Description: {plan.plan_description}")
        print(f"   Total Steps: {len(plan.steps)}")
        print("\n   Workflow:")
        for i, step in enumerate(plan.steps, 1):
            risk_badge = "🟢" if step.risk_level == RiskLevel.READ_ONLY else "🟡"
            print(f"     {i}. {risk_badge} [{step.capability_id}] {step.description}")
    else:
        print(f"\n❌ Plan generation failed")


async def demo_plan_retry_with_remediation() -> None:
    """Demonstrate plan retry with SimpleRemediator."""
    print("\n" + "=" * 60)
    print("Demo 3: Plan Retry with Remediation")
    print("=" * 60)

    from dare_framework.plan import SimpleRemediator

    # Create a workflow with an invalid capability that will fail first attempt
    workflow_steps_first = [
        {
            "capability_id": "cap_invalid",  # This will fail validation
            "params": {},
            "description": "Invalid step",
        },
    ]

    workflow_steps_second = [
        {
            "capability_id": "cap_read",
            "params": {"path": "/valid/path"},
            "description": "Valid read step",
        },
    ]

    # Planner that returns invalid plan first, then valid
    planner = SequentialPlanner(steps_config=workflow_steps_first)
    planner._steps_config = workflow_steps_first  # First attempt

    tool_gateway = MockToolGateway()
    validator = SchemaValidator(tool_gateway=tool_gateway)
    remediator = SimpleRemediator()

    # Custom planner that simulates learning from remediation
    class AdaptivePlanner:
        def __init__(self) -> None:
            self.attempt = 0
            self.name = "adaptive_planner"
            self.component_type = ComponentType.PLANNER

        async def plan(self, ctx: IContext) -> Any:
            self.attempt += 1
            print(f"  [Planner] Attempt {self.attempt}")

            if self.attempt == 1:
                # First attempt: return invalid plan
                from dare_framework.plan.types import ProposedPlan, ProposedStep
                return ProposedPlan(
                    plan_description="Invalid plan",
                    steps=[
                        ProposedStep(
                            step_id="step_1",
                            capability_id="cap_invalid",
                            params={},
                            description="Invalid step",
                        )
                    ],
                    attempt=0,
                )
            else:
                # Second attempt: return valid plan
                from dare_framework.plan.types import ProposedPlan, ProposedStep
                return ProposedPlan(
                    plan_description="Valid plan",
                    steps=[
                        ProposedStep(
                            step_id="step_1",
                            capability_id="cap_read",
                            params={"path": "/valid/path"},
                            description="Read valid file",
                        )
                    ],
                    attempt=1,
                )

    adaptive_planner = AdaptivePlanner()

    loop = PlanLoop(
        planner=adaptive_planner,  # type: ignore[arg-type]
        validator=validator,
        remediator=remediator,
        config=PlanLoopConfig(max_attempts=3, enable_reflection=True),
    )

    ctx = MockContext(config={"task_description": "Adaptive planning demo"})
    milestone = Milestone(
        milestone_id="ms_003",
        description="Adaptive planning",
        user_input="Complete the task (will retry on failure)",
    )

    print(f"\nGenerating plan with adaptive retry:")
    result = await loop.run(milestone, ctx)

    print(f"\n{'✅' if result.success else '❌'} Result:")
    print(f"   Success: {result.success}")
    print(f"   Attempts: {len(result.attempts)}")

    if result.success:
        print(f"   Final plan has {len(result.validated_plan.steps)} step(s)")
    else:
        print(f"   Final reflection: {result.final_reflection[:200]}...")


async def demo_task_to_milestones() -> None:
    """Demonstrate Task to Milestones conversion."""
    print("\n" + "=" * 60)
    print("Demo 4: Task to Milestones")
    print("=" * 60)

    # Create a task with explicit milestones
    task_with_milestones = Task(
        description="Complex project",
        task_id="task_001",
        milestones=[
            Milestone(
                milestone_id="m1",
                description="Phase 1: Research",
                user_input="Research the domain",
            ),
            Milestone(
                milestone_id="m2",
                description="Phase 2: Implementation",
                user_input="Implement the solution",
            ),
            Milestone(
                milestone_id="m3",
                description="Phase 3: Testing",
                user_input="Test and validate",
            ),
        ],
    )

    print(f"\nTask: {task_with_milestones.description}")
    print(f"Milestones:")
    for ms in task_with_milestones.milestones:
        print(f"  - {ms.milestone_id}: {ms.description}")

    # Create a simple task without milestones
    simple_task = Task(
        description="Simple task",
        task_id="task_002",
    )

    print(f"\nSimple Task: {simple_task.description}")
    print(f"Auto-generated milestones: {len(simple_task.to_milestones())}")
    for ms in simple_task.to_milestones():
        print(f"  - {ms.milestone_id}: {ms.description}")


async def main() -> None:
    """Run all demos."""
    print("\n" + "=" * 60)
    print("DARE Framework V4 - Plan Module Examples")
    print("=" * 60)
    print("\nThese examples demonstrate the Plan Loop with mock/deterministic")
    print("components (no LLM API calls required).")

    await demo_simple_planner()
    await demo_sequential_planner()
    await demo_plan_retry_with_remediation()
    await demo_task_to_milestones()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
