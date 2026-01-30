"""Real Model Plan Example - Demonstrates Plan Loop with LLM-based planning.

This example shows how to use the Plan Loop with real LLM-based planners,
validators, and remediators. It requires an OpenAI-compatible API endpoint.

Run:
  # With OpenAI
  export OPENAI_API_KEY="your_key"
  export OPENAI_MODEL="gpt-4o-mini"
  PYTHONPATH=. python examples/plan/real_model_plan_example.py

  # With OpenRouter (default)
  export OPENROUTER_API_KEY="your_key"
  export OPENAI_MODEL="qwen-plus"
  PYTHONPATH=. python examples/plan/real_model_plan_example.py

Key concepts demonstrated:
1. LLMPlanner - LLM-based plan generation
2. SchemaValidator - validating plans against tool schemas
3. LLMRemediator - LLM-based failure analysis
4. PlanLoop - orchestrating with retry and remediation
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio

from dare_framework.context.kernel import IContext, IRetrievalContext
from dare_framework.context.types import AssembledContext, Budget, Message
from dare_framework.infra.component import ComponentType
from dare_framework.model.kernel import IModelAdapter
from dare_framework.model.types import GenerateOptions, ModelInput, ModelResponse
from dare_framework.plan import (
    LLMPlanner,
    LLMRemediator,
    Milestone,
    PlanLoop,
    PlanLoopConfig,
    SchemaValidator,
)
from dare_framework.plan.types import Task
from dare_framework.tool.kernel import IToolGateway
from dare_framework.tool.types import (
    CapabilityDescriptor,
    CapabilityKind,
    CapabilityMetadata,
    CapabilityType,
)


try:
    from langchain_openai import ChatOpenAI
except ImportError:
    print("Error: langchain-openai is required for this example.")
    print("Install with: pip install langchain-openai")
    sys.exit(1)


class LangChainModelAdapter(IModelAdapter):
    """IModelAdapter implementation using LangChain's ChatOpenAI."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.1,
    ) -> None:
        """Initialize with LangChain ChatOpenAI.

        Args:
            model: Model name (e.g., "gpt-4o-mini", "qwen-plus")
            api_key: API key (defaults to env var)
            base_url: API base URL (defaults to env var)
            temperature: Generation temperature
        """
        self._model_name = model or os.getenv("OPENAI_MODEL", "qwen-plus")
        self._api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self._base_url = base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("CHAT_ENDPOINT")
        self._temperature = temperature

        # Initialize LangChain client
        kwargs: dict[str, Any] = {
            "model": self._model_name,
            "temperature": temperature,
        }
        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._base_url:
            kwargs["base_url"] = self._base_url

        self._client = ChatOpenAI(**kwargs)

    @property
    def name(self) -> str:
        return f"langchain_{self._model_name}"

    @property
    def component_type(self) -> ComponentType:
        return ComponentType.MODEL_ADAPTER

    async def generate(
        self,
        model_input: ModelInput,
        *,
        options: GenerateOptions | None = None,
    ) -> ModelResponse:
        """Generate response using LangChain."""
        from langchain_core.messages import (
            AIMessage,
            HumanMessage,
            SystemMessage,
        )

        # Convert messages
        lc_messages = []
        for msg in model_input.messages:
            if msg.role == "system":
                lc_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        # Call model
        response = await self._client.ainvoke(lc_messages)

        return ModelResponse(
            content=response.content,
            usage={
                "model": self._model_name,
            },
        )


class RealContext(IContext):
    """Real context implementation for demonstration."""

    def __init__(
        self,
        task_description: str,
        toollist: list[dict[str, Any]] | None = None,
    ) -> None:
        self._task_description = task_description
        self._config: dict[str, Any] = {
            "task_description": task_description,
        }
        self._messages: list[Message] = []
        self.id = f"ctx_{id(self)}"
        self.budget = Budget(max_tool_calls=10, max_tokens=4000)
        self.short_term_memory = MockRetrievalContext()
        self.long_term_memory = None
        self.knowledge = None
        self.toollist = toollist or []

    def stm_add(self, message: Message) -> None:
        self._messages.append(message)

    def stm_get(self) -> list[Message]:
        return list(self._messages)

    def stm_clear(self) -> list[Message]:
        old = list(self._messages)
        self._messages.clear()
        return old

    def budget_use(self, resource: str, amount: float) -> None:
        current = getattr(self.budget, f"used_{resource}", 0)
        setattr(self.budget, f"used_{resource}", current + amount)

    def budget_check(self) -> None:
        pass

    def budget_remaining(self, resource: str) -> float:
        limit = getattr(self.budget, f"max_{resource}", float("inf"))
        used = getattr(self.budget, f"used_{resource}", 0)
        return limit - used if limit else float("inf")

    def listing_tools(self) -> list[dict[str, Any]]:
        return self.toollist

    def assemble(self, **options: Any) -> AssembledContext:
        return AssembledContext(
            messages=self._messages,
            tools=self.toollist,
            metadata={
                "stage": options.get("stage", "unknown"),
                "task": self._task_description,
            },
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


class FileToolGateway(IToolGateway):
    """Tool gateway with file operation capabilities."""

    def __init__(self, workspace_root: str = ".") -> None:
        self._workspace_root = workspace_root
        self._capabilities: dict[str, CapabilityDescriptor] = {
            "tool_read_file": CapabilityDescriptor(
                id="tool_read_file",
                type=CapabilityType.TOOL,
                name="read_file",
                description="Read the contents of a file at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to read",
                        },
                    },
                    "required": ["path"],
                },
                metadata=CapabilityMetadata(
                    risk_level="read_only",
                    requires_approval=False,
                    capability_kind=CapabilityKind.TOOL,
                ),
            ),
            "tool_write_file": CapabilityDescriptor(
                id="tool_write_file",
                type=CapabilityType.TOOL,
                name="write_file",
                description="Write content to a file at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file to write",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file",
                        },
                    },
                    "required": ["path", "content"],
                },
                metadata=CapabilityMetadata(
                    risk_level="idempotent_write",
                    requires_approval=False,
                    capability_kind=CapabilityKind.TOOL,
                ),
            ),
            "tool_search_code": CapabilityDescriptor(
                id="tool_search_code",
                type=CapabilityType.TOOL,
                name="search_code",
                description="Search for code patterns in the workspace",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern (regex or string)",
                        },
                        "file_extension": {
                            "type": "string",
                            "description": "Optional file extension filter (e.g., '.py')",
                        },
                    },
                    "required": ["pattern"],
                },
                metadata=CapabilityMetadata(
                    risk_level="read_only",
                    requires_approval=False,
                    capability_kind=CapabilityKind.TOOL,
                ),
            ),
            "tool_list_dir": CapabilityDescriptor(
                id="tool_list_dir",
                type=CapabilityType.TOOL,
                name="list_directory",
                description="List files and directories at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the directory",
                        },
                    },
                    "required": ["path"],
                },
                metadata=CapabilityMetadata(
                    risk_level="read_only",
                    requires_approval=False,
                    capability_kind=CapabilityKind.TOOL,
                ),
            ),
        }

    async def list_capabilities(self) -> list[CapabilityDescriptor]:
        return list(self._capabilities.values())

    async def invoke(self, capability_id: str, params: dict[str, Any], *, envelope: Any) -> Any:
        print(f"  [Tool] Would invoke {capability_id} with {params}")
        return {"success": True}

    def register_provider(self, provider: object) -> None:
        pass

    def get_capability(
        self, capability_id: str, *, include_disabled: bool = False
    ) -> CapabilityDescriptor | None:
        return self._capabilities.get(capability_id)


def create_tool_definitions() -> list[dict[str, Any]]:
    """Create tool definitions for the context."""
    gateway = FileToolGateway()
    capabilities = asyncio.run(gateway.list_capabilities())

    tool_defs = []
    for cap in capabilities:
        tool_def = {
            "type": "function",
            "function": {
                "name": cap.id,
                "description": cap.description,
                "parameters": cap.input_schema,
            },
            "capability_id": cap.id,
            "metadata": cap.metadata,
        }
        tool_defs.append(tool_def)

    return tool_defs


async def demo_llm_planner() -> None:
    """Demonstrate LLM-based plan generation."""
    print("\n" + "=" * 70)
    print("Demo 1: LLM-based Plan Generation")
    print("=" * 70)

    # Setup
    model_adapter = LangChainModelAdapter()
    tool_gateway = FileToolGateway()
    tool_defs = create_tool_definitions()

    planner = LLMPlanner(
        model_adapter=model_adapter,
        temperature=0.2,
    )
    validator = SchemaValidator(tool_gateway=tool_gateway)

    loop = PlanLoop(
        planner=planner,
        validator=validator,
        config=PlanLoopConfig(max_attempts=2),
    )

    # Create context with task and available tools
    task_description = (
        "Read the README.md file, then search for all Python files "
        "that contain the word 'TODO', and write a summary of findings "
        "to summary.txt"
    )
    ctx = RealContext(
        task_description=task_description,
        toollist=tool_defs,
    )

    milestone = Milestone(
        milestone_id="ms_llm_001",
        description="Analyze codebase and create summary",
        user_input=task_description,
    )

    print(f"\nTask: {task_description}")
    print(f"Available tools: {len(tool_defs)}")
    print("\nGenerating plan with LLM...")
    print("(This may take a few seconds...)\n")

    result = await loop.run(milestone, ctx)

    if result.success:
        plan = result.validated_plan
        print(f"\n✅ Plan generated successfully!")
        print(f"\n📋 Plan Description: {plan.plan_description}")
        print(f"📊 Total Steps: {len(plan.steps)}")
        print("\n🔧 Execution Steps:")
        for i, step in enumerate(plan.steps, 1):
            risk_emoji = "🟢" if "read_only" in str(step.risk_level) else "🟡"
            print(f"\n  {i}. {risk_emoji} {step.capability_id}")
            print(f"     Description: {step.description}")
            print(f"     Parameters: {step.params}")
            print(f"     Risk Level: {step.risk_level.value}")
    else:
        print(f"\n❌ Plan generation failed after {len(result.attempts)} attempts")
        for attempt in result.attempts:
            print(f"\n  Attempt {attempt.attempt_number}:")
            for error in attempt.validation_errors:
                print(f"    - {error}")


async def demo_llm_planner_with_remediation() -> None:
    """Demonstrate LLM-based planning with remediation on failure."""
    print("\n" + "=" * 70)
    print("Demo 2: LLM-based Planning with Remediation")
    print("=" * 70)

    # Setup
    model_adapter = LangChainModelAdapter()
    tool_gateway = FileToolGateway()
    tool_defs = create_tool_definitions()

    planner = LLMPlanner(
        model_adapter=model_adapter,
        temperature=0.3,
    )
    validator = SchemaValidator(tool_gateway=tool_gateway)
    remediator = LLMRemediator(
        model_adapter=model_adapter,
        temperature=0.2,
    )

    loop = PlanLoop(
        planner=planner,
        validator=validator,
        remediator=remediator,
        config=PlanLoopConfig(max_attempts=3, enable_reflection=True),
    )

    # More complex task that might need retry
    task_description = (
        "Create a comprehensive analysis: 1) List all files in the current directory, "
        "2) Read any markdown files found, 3) Search for configuration patterns, "
        "4) Write a detailed report with findings"
    )
    ctx = RealContext(
        task_description=task_description,
        toollist=tool_defs,
    )

    milestone = Milestone(
        milestone_id="ms_llm_002",
        description="Comprehensive codebase analysis",
        user_input=task_description,
    )

    print(f"\nComplex Task: {task_description}")
    print("\nGenerating plan with LLM and remediation...")
    print("(This may take 10-30 seconds depending on model speed...)\n")

    result = await loop.run(milestone, ctx)

    print(f"\n{'✅' if result.success else '❌'} Result:")
    print(f"   Success: {result.success}")
    print(f"   Total Attempts: {len(result.attempts)}")

    if result.success:
        plan = result.validated_plan
        print(f"   Plan Steps: {len(plan.steps)}")
        print(f"\n   Step Summary:")
        for i, step in enumerate(plan.steps, 1):
            print(f"     {i}. {step.capability_id} - {step.description[:50]}...")
    else:
        print(f"\n   Final Reflection:")
        if result.final_reflection:
            # Print first 500 chars
            print(f"   {result.final_reflection[:500]}...")


async def demo_compare_planners() -> None:
    """Compare deterministic vs LLM planner."""
    print("\n" + "=" * 70)
    print("Demo 3: Comparing Deterministic vs LLM Planner")
    print("=" * 70)

    from dare_framework.plan import SequentialPlanner, SimplePlanner

    tool_gateway = FileToolGateway()
    tool_defs = create_tool_definitions()

    task_description = "Read README.md and summarize its content"

    print(f"\nTask: {task_description}")

    # Deterministic planner
    print("\n--- Deterministic Planner (SimplePlanner) ---")
    simple_planner = SimplePlanner(default_capability_id="tool_read_file")
    simple_validator = SchemaValidator(tool_gateway=tool_gateway)
    simple_loop = PlanLoop(planner=simple_planner, validator=simple_validator)

    ctx = RealContext(task_description=task_description, toollist=tool_defs)
    milestone = Milestone(
        milestone_id="ms_compare",
        description="Compare planners",
        user_input=task_description,
    )

    result = await simple_loop.run(milestone, ctx)

    if result.success:
        plan = result.validated_plan
        print(f"✅ Generated plan with {len(plan.steps)} step(s)")
        for step in plan.steps:
            print(f"   - {step.capability_id}: {step.params}")
    else:
        print("❌ Failed")

    # LLM Planner
    print("\n--- LLM Planner (LLMPlanner) ---")
    print("(This may take a few seconds...)")

    model_adapter = LangChainModelAdapter()
    llm_planner = LLMPlanner(model_adapter=model_adapter, temperature=0.2)
    llm_validator = SchemaValidator(tool_gateway=tool_gateway)
    llm_loop = PlanLoop(planner=llm_planner, validator=llm_validator)

    ctx2 = RealContext(task_description=task_description, toollist=tool_defs)

    result2 = await llm_loop.run(milestone, ctx2)

    if result2.success:
        plan = result2.validated_plan
        print(f"✅ Generated plan with {len(plan.steps)} step(s)")
        for i, step in enumerate(plan.steps, 1):
            print(f"   {i}. {step.capability_id}")
            print(f"      Description: {step.description}")
            print(f"      Params: {step.params}")
    else:
        print("❌ Failed")

    print("\n📊 Comparison:")
    print("   - SimplePlanner: Fast, predictable, limited flexibility")
    print("   - LLMPlanner: Slower, adaptive, handles complex tasks")


async def main() -> None:
    """Run all demos."""
    print("\n" + "=" * 70)
    print("DARE Framework V4 - Real Model Plan Examples")
    print("=" * 70)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n⚠️  Warning: No API key found!")
        print("Please set one of:")
        print("  - OPENAI_API_KEY (for OpenAI)")
        print("  - OPENROUTER_API_KEY (for OpenRouter)")
        print("\nUsing default configuration which may fail.")
        print("\nPress Enter to continue anyway, or Ctrl+C to exit...")
        try:
            input()
        except KeyboardInterrupt:
            print("\nExiting...")
            return

    model = os.getenv("OPENAI_MODEL", "qwen-plus")
    print(f"\nConfiguration:")
    print(f"  Model: {model}")
    print(f"  API Key: {'✓ Set' if api_key else '✗ Not set'}")

    try:
        await demo_llm_planner()
    except Exception as e:
        print(f"\n❌ Demo 1 failed: {e}")
        import traceback
        traceback.print_exc()

    # Uncomment to run more demos (they cost more tokens)
    # try:
    #     await demo_llm_planner_with_remediation()
    # except Exception as e:
    #     print(f"\n❌ Demo 2 failed: {e}")

    try:
        await demo_compare_planners()
    except Exception as e:
        print(f"\n❌ Demo 3 failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("Demos completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
