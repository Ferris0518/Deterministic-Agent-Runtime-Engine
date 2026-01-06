## ADDED Requirements
### Requirement: Interface Partitioning
Core interface protocols SHALL be split into domain-focused modules under `dare_framework/core/` (runtime, planning, policy, tooling, validation, trust boundary, context, MCP, config, registries, and composition).

#### Scenario: Finding an interface
- **WHEN** a contributor looks for `IToolRuntime`
- **THEN** it is located in the tooling domain module under `dare_framework/core/` alongside related tool contracts.

### Requirement: Tool Registry Interface
The framework SHALL define an `IToolRegistry` interface in the core infrastructure layer to represent the trusted source of tool metadata used by TrustBoundary and policy enforcement, with explicit methods for retrieving tool definitions.

#### Scenario: Registry contract lookup
- **WHEN** TrustBoundary needs a tool definition for a proposed step
- **THEN** it retrieves the definition via `IToolRegistry` rather than accessing concrete registry implementations directly.

#### Scenario: Listing trusted tools
- **WHEN** a component needs the current set of trusted tool definitions
- **THEN** it calls `IToolRegistry.list_tool_definitions()` (or equivalent) instead of enumerating concrete tool instances.

### Requirement: Tool Registry Minimal Contract
The `IToolRegistry` interface SHALL expose a minimal contract that includes:
- retrieving a tool definition by name
- listing all tool definitions

#### Scenario: Resolving a tool by name
- **WHEN** TrustBoundary validates a proposed step by tool name
- **THEN** it calls the registry method that returns a `ToolDefinition` or a clear "not found" result.

#### Scenario: Minimal method shape
- **WHEN** a contributor reads the `IToolRegistry` interface
- **THEN** it includes methods equivalent to `get_tool_definition(name: str) -> ToolDefinition | None` and `list_tool_definitions() -> list[ToolDefinition]`.

### Requirement: Interface Intent Documentation
Each core interface and each abstract method SHALL include a concise design-intent docstring or comment that explains its role, trust boundary, or layer responsibility, referencing the design docs where relevant.

#### Scenario: Reading an interface contract
- **WHEN** a contributor reads `IPolicyEngine`
- **THEN** the interface includes a short note describing its enforcement role per the design docs.
