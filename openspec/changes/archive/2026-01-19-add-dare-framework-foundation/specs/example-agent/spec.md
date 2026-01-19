## ADDED Requirements
### Requirement: Framework-Backed Coding Agent Example
The example coding agent SHALL be built using AgentBuilder and SHALL register the example tools and skills from `examples/coding-agent/`.

#### Scenario: Example agent instantiation
- **WHEN** a developer instantiates the coding agent
- **THEN** it composes AgentBuilder with the example tools and skills

### Requirement: Deterministic Mock Mode
The example agent SHALL support a deterministic mode that uses a MockModelAdapter and/or DeterministicPlanGenerator to avoid external LLM calls.

#### Scenario: Mocked run
- **WHEN** the agent runs in deterministic mode
- **THEN** it completes the workflow without network access and returns fixed outputs

### Requirement: Optional Real Model Adapter
The example agent SHALL allow configuration of a real IModelAdapter, and this path SHALL remain optional and non-default.

#### Scenario: Real model configured
- **WHEN** a user configures a real model adapter
- **THEN** the agent delegates plan/execute generation to that adapter

### Requirement: Example Flow Validation
The example agent SHALL include tests or scripts that validate the end-to-end flow using the deterministic mode.

#### Scenario: Example flow test
- **WHEN** the example flow test is executed
- **THEN** it completes without external dependencies and asserts a successful RunResult
