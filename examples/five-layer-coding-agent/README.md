# Five-Layer Coding Agent Example

This example demonstrates the complete five-layer loop architecture using `FiveLayerAgent` from the DARE Framework.

## Architecture

The agent implements the full five-layer orchestration loop:

1. **Session Loop** - Top-level task lifecycle
2. **Milestone Loop** - Sub-goal tracking and verification
3. **Plan Loop** - Plan generation and validation
4. **Execute Loop** - Model-driven execution
5. **Tool Loop** - Individual tool invocations

```
┌─────────────────────────────────────────────────────────────────┐
│  Session Loop (跨 Context Window)                                │
│  └─ Milestone Loop (Observe → Plan → Approve → Execute → Verify) │
│     ├─ Plan Loop (生成有效计划，失败不外泄)                        │
│     ├─ Execute Loop (LLM 驱动执行)                               │
│     └─ Tool Loop (WorkUnit 内部闭环)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
five-layer-coding-agent/
├── README.md                    # This file
├── __init__.py
├── .env                         # Environment variables (DO NOT COMMIT)
├── .env.example                 # Environment template (safe to commit)
├── tools/                       # Tool imports from dare_framework
│   └── __init__.py
├── planners/                    # Planner implementations
│   ├── deterministic.py         # For testing without model calls
│   └── __init__.py
├── validators/                  # Validator implementations
│   ├── simple_validator.py     # Basic validation logic
│   └── __init__.py
├── model_adapters/              # Model adapters
│   ├── openrouter.py            # OpenRouter API adapter
│   └── __init__.py
├── deterministic_agent.py       # Deterministic mode entry point
├── openrouter_agent.py          # OpenRouter mode entry point (TODO)
└── workspace/                   # Test workspace
    ├── sample.py                # Sample Python file
    └── sample_test.py           # Sample test file
```

## Tools

The example uses built-in tools from `dare_framework.tool`:

- **ReadFileTool** - Read file contents (READ_ONLY risk level)
- **WriteFileTool** - Write file contents (IDEMPOTENT_WRITE risk level)
- **SearchCodeTool** - Search code patterns (READ_ONLY risk level)
- **RunCommandTool** - Execute commands (NON_IDEMPOTENT_EFFECT risk level)
- **EditLineTool** - Edit specific lines (IDEMPOTENT_WRITE risk level)

## Running the Example

### Deterministic Mode (No Model Calls)

Perfect for testing and CI environments:

```bash
# From project root
PYTHONPATH=. python examples/five-layer-coding-agent/deterministic_agent.py
```

This mode uses a predefined plan and doesn't require an API key.

### OpenRouter Mode (Real Model)

Uses OpenRouter API with free models:

#### 1. Setup Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and add your OpenRouter API key
nano .env
```

Your `.env` should look like:
```bash
OPENROUTER_API_KEY=sk-or-v1-your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free
```

**⚠️ IMPORTANT SECURITY NOTE:**
- **NEVER commit your `.env` file** - it's already in `.gitignore`
- Only commit `.env.example` (the template)
- Keep your API keys secret

#### 2. Install Dependencies

```bash
pip install openai python-dotenv
```

#### 3. Run OpenRouter Agent

```bash
# From project root
PYTHONPATH=. python examples/five-layer-coding-agent/openrouter_agent.py
```

## Recommended Free Models

OpenRouter provides several free models for testing:

- `xiaomi/mimo-v2-flash:free` - Fast, good for testing (recommended)
- `google/gemini-flash-1.5-8b-exp-0827:free` - Good quality
- `meta-llama/llama-3.2-3b-instruct:free` - Smaller model

Update `OPENROUTER_MODEL` in your `.env` file to try different models.

## Example Task Scenarios

### Scenario 1: Code Search
Read a file and search for TODO comments.

### Scenario 2: Test Execution
Run pytest tests and report results.

### Scenario 3: Code Modification
Edit a file to implement a missing function.

## Known Limitations

This is an example implementation with the following limitations:

- **Simple Validator** - Basic validation logic, not production-ready
- **No HITL Integration** - Human-in-the-loop is mocked
- **Limited Error Handling** - Basic error messages only
- **No Security Boundary** - `ISecurityBoundary` not fully implemented

See `openspec/changes/add-five-layer-example/design.md` for more details on design gaps.

## Troubleshooting

### "ModuleNotFoundError: No module named 'dare_framework'"

Run from project root with `PYTHONPATH=.`:
```bash
PYTHONPATH=. python examples/five-layer-coding-agent/deterministic_agent.py
```

### "OpenRouter API key is required"

Make sure you've created `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### "milestone failed after max attempts"

This usually means the validator couldn't verify the milestone. Check:
- Tool execution succeeded
- Plan steps are correct
- Validator logic matches your expectations

## Development

To modify this example:

1. Edit planners to change planning strategy
2. Edit validators to change verification logic
3. Add more tools to extend capabilities
4. Modify agents to change task scenarios

## References

- [DARE Framework Documentation](../../doc/design/)
- [Five-Layer Loop Design](../../doc/design/Architecture.md)
- [OpenSpec Proposal](../../openspec/changes/add-five-layer-example/)
- [OpenRouter API](https://openrouter.ai/)
