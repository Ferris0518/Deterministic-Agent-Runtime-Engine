## MODIFIED Requirements
### Requirement: Security Boundary Interface
The framework SHALL define an `ISecurityBoundary` interface in the kernel layer to derive safety-critical fields from trusted registries before policy checks, with explicit methods for deriving validated steps or plans.

#### Scenario: Deriving safety fields
- **WHEN** a proposed plan step is supplied by the model
- **THEN** `ISecurityBoundary` derives tool type, risk level, and approval requirements from trusted registries and outputs a validated step.

#### Scenario: Deriving a validated plan
- **WHEN** a proposed plan is supplied by the model
- **THEN** `ISecurityBoundary` exposes a method that returns a `ValidatedPlan` built from trusted tool metadata.

### Requirement: Security Boundary Minimal Contract
The `ISecurityBoundary` interface SHALL expose a minimal contract that includes:
- deriving a validated step from a proposed step and registry data
- deriving a validated plan from a proposed plan and registry data

#### Scenario: Validating a step in isolation
- **WHEN** a component needs to validate a single proposed step
- **THEN** SecurityBoundary provides a method that returns a `ValidatedStep` or a structured error.

#### Scenario: Minimal method shape
- **WHEN** a contributor reads the `ISecurityBoundary` interface
- **THEN** it includes methods equivalent to `derive_step(proposed_step: ProposedStep, registry: IToolRegistry) -> ValidatedStep` and `derive_plan(proposed_plan: ProposedPlan, registry: IToolRegistry) -> ValidatedPlan`.

### Requirement: Trust Boundary Positioning
The runtime validation flow SHALL apply `ISecurityBoundary` before policy enforcement and execution.

#### Scenario: Enforcing ordering
- **WHEN** the runtime validates a plan
- **THEN** SecurityBoundary runs before `IPolicyEngine` checks and before any tool execution path.
