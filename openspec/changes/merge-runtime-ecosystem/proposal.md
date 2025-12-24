# Change: merge runtime ecosystem with main flow

## Why
The current branch implements the main Session/Milestone flow but lacks the assembly and persistence features from the init branch, leaving tools, examples, and auditability incomplete. We need to merge both sets of strengths so the runtime is both operationally complete and aligned with the new main flow.

## What Changes
- Add an Agent/AgentBuilder assembly layer with tool/skill registries and optional MCP-backed tools.
- Add file-backed EventLog and Checkpoint implementations (retain in-memory defaults).
- Enhance ToolRuntime to support WorkUnit envelopes, DonePredicate loops, and plan tool detection.
- Wire hook callbacks for tool calls and update examples/tests to use the merged APIs.

## Impact
- Affected specs: agent-assembly, runtime-storage, tool-runtime
- Affected code: dare_framework/components/, dare_framework/core/runtime.py, dare_framework/__init__.py, examples/coding-agent/, tests/
