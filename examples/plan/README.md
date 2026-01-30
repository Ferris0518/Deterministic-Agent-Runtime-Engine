# Plan Module Examples

This directory demonstrates the DARE Framework V4 Plan module, showcasing both deterministic and LLM-based planning capabilities.

## Overview

The Plan module implements the **Plan Loop** (Layer 3 of the five-layer architecture):

```
Plan Loop:
  1. Generate plan (IPlanner)
  2. Validate plan (IValidator)
  3. If valid → return ValidatedPlan
  4. If invalid → remediate (IRemediator) and retry
```

Key design principles:
- **Plan Attempt Isolation**: Failed attempts don't pollute outer state
- **Proposed vs Validated**: Clear separation between untrusted (LLM) and trusted (validated) plans
- **Trusted Fields**: Risk levels derived from registry, not LLM output

## Files

| File | Description |
|------|-------------|
| `mock_plan_example.py` | Deterministic planning without LLM calls |
| `real_model_plan_example.py` | LLM-based planning with real API calls |

## Running Examples

### Mock Example (No API Key Required)

```bash
PYTHONPATH=. python examples/plan/mock_plan_example.py
```

This demonstrates:
- `SimplePlanner` - Single-step deterministic plans
- `SequentialPlanner` - Multi-step workflows
- `SchemaValidator` - Plan validation against tool schemas
- `SimpleRemediator` - Rule-based failure guidance
- `PlanLoop` - Retry logic with attempt isolation

### Real Model Example (API Key Required)

```bash
# Option 1: OpenAI
export OPENAI_API_KEY="your_key"
export OPENAI_MODEL="gpt-4o-mini"
PYTHONPATH=. python examples/plan/real_model_plan_example.py

# Option 2: OpenRouter (default)
export OPENROUTER_API_KEY="your_key"
export OPENAI_MODEL="qwen-plus"
PYTHONPATH=. python examples/plan/real_model_plan_example.py
```

This demonstrates:
- `LLMPlanner` - LLM-based plan generation
- `SchemaValidator` - Validation of LLM-generated plans
- `LLMRemediator` - LLM-based failure analysis
- Comparison of deterministic vs LLM planners

## Key Concepts

### 1. Planners (IPlanner)

Generate `ProposedPlan` from task context:

```python
# Deterministic
planner = SimplePlanner(default_capability_id="cap_read")

# LLM-based
planner = LLMPlanner(model_adapter=model_adapter)

# Multi-step workflow
planner = SequentialPlanner(steps_config=[
    {"capability_id": "cap_search", "params": {"pattern": "TODO"}},
    {"capability_id": "cap_read", "params": {"path": "/file.txt"}},
])
```

### 2. Validators (IValidator)

Transform `ProposedPlan` → `ValidatedPlan`:

```python
validator = SchemaValidator(tool_gateway=tool_gateway)
validated = await validator.validate_plan(proposed_plan, ctx)

# validated.success: bool
# validated.steps: List[ValidatedStep] with trusted risk_level
```

**Critical**: Risk levels are derived from `CapabilityDescriptor.metadata` (trusted registry), NOT from LLM output.

### 3. Remediators (IRemediator)

Generate guidance when validation fails:

```python
# Rule-based
remediator = SimpleRemediator()

# LLM-based
remediator = LLMRemediator(model_adapter=model_adapter)

reflection = await remediator.remediate(verify_result, ctx)
# reflection is added to context for next plan attempt
```

### 4. PlanLoop

Orchestrates plan generation with retry:

```python
loop = PlanLoop(
    planner=planner,
    validator=validator,
    remediator=remediator,
    config=PlanLoopConfig(max_attempts=3),
)

result = await loop.run(milestone, ctx)
# result.success: bool
# result.validated_plan: ValidatedPlan | None
# result.attempts: List[PlanAttemptRecord]
```

## Plan Attempt Isolation

A key constraint of the Plan Loop: **failed plan attempts must not contaminate milestone/session state**.

- Failed attempts are recorded in `result.attempts`
- Only validated plans proceed to execution
- Remediation guidance can be added to context for next attempt
- Event log captures all attempts for audit

## Example Output

### Mock Example Output

```
============================================================
Demo 1: SimplePlanner - Single Step Plan
============================================================

Generating plan for: Read the configuration from /etc/config.json
  [Context] Plan attempt: 0

✅ Plan generated successfully!
   Description: Execute: Read the configuration from /etc/config.json
   Steps: 1
     1. [read_only] cap_read
        Params: {'description': 'Read the configuration from /etc/config.json'}
```

### Real Model Example Output

```
============================================================
Demo 1: LLM-based Plan Generation
============================================================

Task: Read the README.md file, then search for all Python files...
Available tools: 4

Generating plan with LLM...
(This may take a few seconds...)

✅ Plan generated successfully!

📋 Plan Description: Multi-step analysis workflow
📊 Total Steps: 4

🔧 Execution Steps:

  1. 🟢 tool_list_directory
     Description: List files in the workspace
     Parameters: {'path': '.'}
     Risk Level: read_only

  2. 🟢 tool_read_file
     Description: Read README.md contents
     Parameters: {'path': 'README.md'}
     Risk Level: read_only
     
  ...
```

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│ Plan Module (dare_framework/plan/)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Types (types.py)                                           │
│    - Task, Milestone, ProposedPlan, ValidatedPlan           │
│    - ProposedStep, ValidatedStep                            │
│    - Envelope, DonePredicate                                │
│                                                             │
│  Interfaces (interfaces.py)                                 │
│    - IPlanner.plan(ctx) → ProposedPlan                      │
│    - IValidator.validate_plan(plan, ctx) → ValidatedPlan    │
│    - IRemediator.remediate(result, ctx) → str               │
│                                                             │
│  Internal Implementations (_internal/)                      │
│    - SimplePlanner, SequentialPlanner                       │
│    - LLMPlanner                                             │
│    - SchemaValidator, PermissiveValidator                   │
│    - CompositeValidator                                     │
│    - LLMRemediator, SimpleRemediator, NoOpRemediator        │
│    - PlanLoop                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Integration Points                                          │
├─────────────────────────────────────────────────────────────┤
│  IContext        ← Context for plan generation              │
│  IToolGateway    ← Capability registry for validation       │
│  IModelAdapter   ← LLM for LLMPlanner/LLMRemediator         │
│  IEventLog       ← Audit logging (optional)                 │
└─────────────────────────────────────────────────────────────┘
```

## Testing

Run the unit tests:

```bash
pytest tests/unit/plan/ -v
```

Test coverage:
- `test_simple_planner.py` - Deterministic planners
- `test_llm_planner.py` - LLM-based planner
- `test_schema_validator.py` - Plan validation
- `test_llm_remediator.py` - Remediation strategies
- `test_plan_loop.py` - Retry logic and isolation

## Next Steps

To integrate the Plan module into your agent:

1. **Choose a Planner**: Start with `SimplePlanner` for testing, upgrade to `LLMPlanner` for flexibility
2. **Configure Validation**: Use `SchemaValidator` with your `IToolGateway`
3. **Add Remediation**: Use `LLMRemediator` for complex failures, `SimpleRemediator` for speed
4. **Set up Event Logging**: Pass `IEventLog` to `PlanLoop` for audit
5. **Tune Retry**: Adjust `PlanLoopConfig.max_attempts` based on your use case
