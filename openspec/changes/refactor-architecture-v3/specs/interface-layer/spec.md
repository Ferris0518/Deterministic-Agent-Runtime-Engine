## MODIFIED Requirements
### Requirement: Shared types are v2-aligned
The system SHALL locate shared canonical types (evidence, risk levels, tool results/definitions, model message types) under `dare_framework3.types` and SHALL use them across kernel, components, and examples.

#### Scenario: Tool loop returns canonical ToolResult
- **GIVEN** a tool invocation through the v3 Tool Loop
- **WHEN** it completes
- **THEN** the result is represented using the canonical `ToolResult` type from `dare_framework3.types`.

### Requirement: Core Interface Coverage
The interface layer SHALL define the Kernel contracts and component interfaces, including:

- Kernel: `IRunLoop`, `ILoopOrchestrator`, `IExecutionControl`, `IContextManager`, `IResourceManager`, `IEventLog`, `IToolGateway`, `ISecurityBoundary`, `IExtensionPoint`
- Strategies: `IPlanner`, `IValidator`, `IRemediator`, `IContextStrategy`
- Capabilities: `IModelAdapter`, `IMemory`, `IRetriever`, `IIndexer`, `IPromptStore`, `ICapabilityProvider`
- Security components: `ITrustVerifier`, `IPolicyEngine`, `ISandbox`

#### Scenario: Developer implements a custom Kernel component
- **WHEN** a developer imports and implements any Kernel interface
- **THEN** the contract surface is available, typed, and usable for composition.

### Requirement: Core Data Models
The interface layer SHALL provide canonical data models for v3, including:
`CapabilityDescriptor`, `CapabilityType`, `Envelope`, `Budget`, `DonePredicate`, `Checkpoint`, `ContextPacket`, security policy models, and task/milestone/run result models used by the Kernel flow.

#### Scenario: Kernel and providers exchange canonical models
- **WHEN** a capability is discovered and invoked through the gateway
- **THEN** capability descriptors and envelopes use the canonical models (no protocol-specific leakage).

### Requirement: AgentBuilder Composition API
The developer API (AgentBuilder or equivalent) SHALL support composing:
Kernel defaults, strategies (planner/validator/remediator/context strategy), tools and providers, optional protocol adapters, memory, explicit budgets, and presets.

#### Scenario: Minimal v3 build and run
- **WHEN** a developer builds an agent with Kernel defaults and a minimal tool set
- **THEN** the agent can execute a deterministic end-to-end flow without external network dependencies.
