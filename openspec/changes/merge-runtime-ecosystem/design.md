## Context
The current runtime implements the Session/Milestone/Plan/Execute loop but removed the init branch's assembly, persistence, and integration features. We need to reintroduce these capabilities without regressing the new runtime architecture.

## Goals / Non-Goals
- Goals:
  - Provide a builder-based assembly path for tools, skills, and models.
  - Restore file-backed EventLog and Checkpoint for auditability.
  - Ensure ToolRuntime supports WorkUnit envelopes and plan tools.
  - Keep default components lightweight and testable.
- Non-Goals:
  - Full production-grade storage backends (e.g., Postgres/S3).
  - Comprehensive MCP orchestration beyond basic tool bridging.

## Decisions
- Keep the current Session/Milestone runtime as the primary loop and add assembly layers on top.
- Implement file-backed persistence as optional components alongside in-memory defaults.
- Extend DefaultToolRuntime with optional skill registry and workunit support without breaking existing signatures.

## Risks / Trade-offs
- Added surface area increases maintenance; mitigate with focused tests and minimal APIs.
- Optional MCP integration may add dependency complexity; keep imports lazy and guard when SDK is missing.

## Migration Plan
- Update examples to use the merged assembly/runtime APIs.
- Add tests covering the new builder, persistence components, and tool runtime behavior.

## Open Questions
- Should tool call hooks include tool input/output redaction for sensitive data?
