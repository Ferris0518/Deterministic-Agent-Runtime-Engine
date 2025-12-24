## 1. Core skeleton + runtime flow (first milestone)
- [ ] 1.1 Scaffold `agent_framework/` package layout and define core data models (Task, Milestone, RunContext, Envelope, DonePredicate, Plan, ValidatedPlan, ToolResult, RunResult, PolicyDecision, RuntimeState).
- [ ] 1.2 Define core interfaces per UML A.1 and v1.1 (IRuntime, IEventLog, IToolRuntime, IPolicyEngine, IPlanGenerator, IValidator, IRemediator, ISkillRegistry, IContextAssembler, IModelAdapter, IToolkit, ITool, ISkill, IMemory, IHook, ICheckpoint).
- [ ] 1.3 Implement LocalEventLog (append-only JSONL + hash chain) and file-backed ICheckpoint for observability/debugging.
- [ ] 1.4 Implement AgentRuntime state machine and five-layer flow using small loop helpers (Plan/Execute/Tool) to avoid monolithic pseudocode while preserving v1.3 semantics.
- [ ] 1.5 Provide minimal stub/default implementations for PolicyEngine, PlanGenerator, Validator, Remediator, ContextAssembler to enable deterministic flow with mocks.

## 2. Interface layer assembly
- [ ] 2.1 Implement registries (ToolRegistry, SkillRegistry) and Toolkit surface.
- [ ] 2.2 Implement ToolRuntime with policy checks, plan-tool detection, and envelope-aware Tool Loop entry.
- [ ] 2.3 Implement AgentBuilder composition API with quick_start and component overrides.
- [ ] 2.4 Define MCP interfaces (IMCPClient) and MCPToolkit stub; ensure no MCP config is required for default runtime.

## 3. Example coding agent
- [ ] 3.1 Add MockModelAdapter and/or DeterministicPlanGenerator fixtures for deterministic runs.
- [ ] 3.2 Wire `examples/coding-agent/` to AgentBuilder with a switch for mock vs real adapters.
- [ ] 3.3 Add deterministic example tests covering a full run without network dependencies.

## 4. Validation
- [ ] 4.1 Unit tests for runtime state transitions and event log hash-chain verification.
- [ ] 4.2 Integration test for end-to-end flow using the example agent in deterministic mode.

## Dependencies / Parallelism
- 1.x must complete before 2.x and 3.x.
- 2.4 can run in parallel with 2.1-2.3 once interfaces are defined.
- 4.x depends on 1-3.
