# component-management Specification

## Purpose
TBD - created by archiving change add-component-manager-entrypoints. Update Purpose after archive.
## Requirements
### Requirement: Component lifecycle interface
The system SHALL define `IComponent` with an `order` attribute, an async `init()` hook, a `register()` hook, and an async `close()` hook. Layer 2 pluggable interfaces MUST implement or extend `IComponent` (IModelAdapter, IMemory, IValidator, ITool, ISkill, IMCPClient, IHook, IConfigProvider, IPromptStore).

#### Scenario: Managed component lifecycle
- **WHEN** ComponentManager instantiates a component discovered via entry points
- **THEN** it MUST call `init()` before `register()` and MUST call `close()` on shutdown

#### Scenario: Pluggable interface conformance
- **WHEN** a Layer 2 implementation provides IModelAdapter or IMemory functionality
- **THEN** it MUST implement `IComponent` to participate in ordering and registration

### Requirement: Component discovery via entry points
The system SHALL support entry point discovery for pluggable components via per-interface managers (Validator/Memory/ModelAdapter/Tool/Skill/MCPClient/Hook/ConfigProvider/PromptStore). Each manager SHALL inherit BaseComponentManager and return an ordered list of its managed components when provided an IConfigProvider.

#### Scenario: Validator manager discovery
- **WHEN** ValidatorManager loads entry points
- **THEN** it MUST return a list of IValidator ordered by ascending IComponent.order

#### Scenario: Memory manager discovery
- **WHEN** MemoryManager loads entry points with an IConfigProvider
- **THEN** it MUST initialize and register IMemory components and return the ordered list

### Requirement: Ordered registration
The system SHALL order discovered components by ascending `order` value before initialization and registration.

#### Scenario: Order determines precedence
- **WHEN** two components are discovered with `order` values of 10 and 50
- **THEN** the component with order 10 MUST initialize and register first

### Requirement: Lifecycle ownership boundary
The system SHALL only manage lifecycle (init/close) for components it creates and MUST NOT close externally injected component instances.

#### Scenario: Caller-injected component
- **WHEN** a caller injects a component instance directly into AgentBuilder
- **THEN** ComponentManager MUST register it but MUST NOT call `close()` automatically

### Requirement: Composite tool assembly
ToolManager SHALL support registering composite tools defined by configuration recipes (name, optional description, ordered steps referencing existing tools).

#### Scenario: Composite tool from config
- **WHEN** config defines `composite_tools` with a recipe containing `steps` referencing known tools
- **THEN** ToolManager assembles and registers a CompositeTool that executes the referenced tools sequentially

