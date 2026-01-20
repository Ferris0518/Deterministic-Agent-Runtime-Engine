## MODIFIED Requirements
### Requirement: Interface Partitioning
Core interface protocols SHALL be exposed from the stable interface facade (`dare_framework3/interfaces/`) and organized internally by domain under `dare_framework3/_internal/<domain>/kernel.py` and `components.py` (execution, context, security, tool, plan, model, protocols).

#### Scenario: Finding an interface
- **WHEN** a contributor looks for `IToolGateway`
- **THEN** it is available from `dare_framework3.interfaces` and defined in `dare_framework3/_internal/tool/kernel.py`.

### Requirement: Tool Registry Interface
The framework SHALL define an `IToolRegistry` interface in the stable interface layer to represent the trusted source of tool metadata used by security and policy enforcement.

#### Scenario: Registry contract lookup
- **WHEN** SecurityBoundary needs a tool definition for a proposed step
- **THEN** it retrieves the definition via `IToolRegistry` rather than accessing concrete registry implementations directly.

### Requirement: Tool Registry Minimal Contract
The `IToolRegistry` interface SHALL expose a minimal contract that includes:
- retrieving a tool definition by name
- listing all tool definitions

#### Scenario: Resolving a tool by name
- **WHEN** SecurityBoundary validates a proposed step by tool name
- **THEN** it calls the registry method that returns a `ToolDefinition` or a clear "not found" result.

### Requirement: Interface Intent Documentation
Each core interface and each abstract method SHALL include a concise design-intent docstring or comment that explains its role, trust boundary, or layer responsibility.

#### Scenario: Reading an interface contract
- **WHEN** a contributor reads `IPolicyEngine`
- **THEN** the interface includes a short note describing its enforcement role per the design docs.
