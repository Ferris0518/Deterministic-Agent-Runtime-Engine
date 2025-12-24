## Context
DARE v1.3 defines a five-layer runtime loop with explicit state transitions, trust boundaries, and audit logging. The interface layer v1.1 defines the component boundaries (including MCP integration) and agent composition. We need a minimal but functional foundation that can run the example coding agent deterministically while keeping interfaces complete and stable.

## Goals / Non-Goals
- Goals:
  - Implement the five-layer runtime flow (Session, Milestone, Plan, Execute, Tool) with explicit state transitions.
  - Provide a working LocalEventLog for observability and debugging.
  - Define all core interfaces listed in v1.3 UML A.1 and v1.1 interface design, including IModelAdapter.
  - Ship an example coding agent that can run in deterministic/mock mode, with optional real model adapters.
  - Keep MCP integration optional and interface-only for the initial milestone.
- Non-Goals:
  - Full production-grade MCP clients or external LLM integrations.
  - Distributed storage, remote checkpointing, or performance optimizations.
  - Complete implementations of advanced validators or policy engines beyond baseline flow.

## Decisions
- Runtime structure: implement IRuntime as a small state machine orchestrator that delegates to helper functions/classes for each loop (Plan, Execute, Tool) to avoid monolithic pseudocode and allow targeted tests.
- Event logging: LocalEventLog is required for all loop transitions and tool invocations; hash-chain verification is included in the minimal implementation.
- Interface coverage: define all interfaces from UML A.1, and include data models used by the loop (RunContext, Envelope, DonePredicate, Plan/ValidatedPlan, RunResult, ToolResult, etc.).
- Mocking strategy: provide both a MockModelAdapter (fixed responses) and a DeterministicPlanGenerator for deterministic tests; real adapters remain optional.
- MCP: define IMCPClient and MCPToolkit in the interface layer, but only provide a no-op or stub implementation until MCP work is prioritized.

## Risks / Trade-offs
- Translating pseudocode directly into runtime flow can lead to hard-to-test logic. Mitigation: enforce small, single-responsibility loop helpers with explicit inputs/outputs.
- Keeping MCP interface-only delays full integration; acceptable for MVP with clear extension points.

## Migration Plan
1. Introduce interface definitions and core data models.
2. Implement LocalEventLog and IRuntime orchestration scaffolding.
3. Wire example coding agent in deterministic mode.
4. Expand to real model adapters and MCP implementation in subsequent changes.

## Open Questions
- Which minimal policy checks are required for the first runtime milestone (deny/allow only, or approval flow)?
- Should the first release include a real PlanGenerator or only deterministic/mocked generation?
