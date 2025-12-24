## ADDED Requirements
### Requirement: Agent assembly builder
The system SHALL provide an AgentBuilder that assembles an AgentRuntime from registered tools, skills, and configured components, returning an Agent that can run Tasks.

#### Scenario: Build an agent with tools
- **WHEN** the builder is configured with at least one tool and a model adapter
- **THEN** calling build returns an agent that can execute a Task through the runtime

### Requirement: Tool and skill registries
The system SHALL provide registries for tools and skills that support registration and lookup by name.

#### Scenario: Register and retrieve tools
- **WHEN** a tool is registered in the registry
- **THEN** it can be retrieved by name and listed in registry output

### Requirement: In-memory memory implementation
The system SHALL provide a default in-memory memory store implementing the memory interface.

#### Scenario: Store and search memory
- **WHEN** a memory item is stored
- **THEN** a search returns the stored item when the query matches

### Requirement: Optional MCP toolkit integration
The system SHALL allow MCP clients to expose tools that can be registered into the tool registry when MCP support is configured.

#### Scenario: MCP tool registration
- **WHEN** an MCP client lists tools
- **THEN** the toolkit exposes them as registered tools available to the runtime
