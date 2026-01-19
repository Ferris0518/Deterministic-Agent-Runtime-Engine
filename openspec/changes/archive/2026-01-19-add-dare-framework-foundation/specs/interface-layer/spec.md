## ADDED Requirements
### Requirement: Core Interface Coverage
The interface layer SHALL define the core interfaces from UML A.1 and the v1.1 interface design, including: IRuntime, IEventLog, IToolRuntime, IPolicyEngine, IPlanGenerator, IValidator, IRemediator, ISkillRegistry, IContextAssembler, IModelAdapter, IToolkit, ITool, ISkill, IMemory, IHook, and ICheckpoint.

#### Scenario: Developer implements a custom component
- **WHEN** a developer imports and implements any listed interface
- **THEN** the interface surface is available and stable for composition

### Requirement: Core Data Models
The interface layer SHALL provide stable data models for runtime flow, including Task, Milestone, RunContext, Envelope, DonePredicate, Plan, ValidatedPlan, ToolResult, RunResult, PolicyDecision, and RuntimeState.

#### Scenario: Runtime consumes model types
- **WHEN** the runtime or tools exchange inputs and outputs
- **THEN** they use these shared data models without ad-hoc structures

### Requirement: AgentBuilder Composition API
AgentBuilder SHALL compose runtime, model adapters, tools, skills, memory, hooks, and MCP clients, and SHALL offer a quick_start constructor for minimal configuration.

#### Scenario: Minimal agent build
- **WHEN** a user calls AgentBuilder.quick_start with a name and model
- **THEN** a runnable agent is returned using default components

### Requirement: Optional MCP Integration Surface
The interface layer SHALL define IMCPClient and MCPToolkit, and MCP integration SHALL keep the default runtime functional when no MCP clients are configured.

#### Scenario: MCP is not configured
- **WHEN** no MCP clients are provided
- **THEN** the runtime operates with local tools only and does not attempt MCP discovery
