## ADDED Requirements
### Requirement: LLM-driven execute loop
The runtime SHALL invoke the configured `IModelAdapter` during the execute loop, provide the assembled prompt and available tool definitions, and iterate over tool calls until the model returns a final response.

#### Scenario: Model returns a final response
- **WHEN** the model response contains no tool calls
- **THEN** the execute loop returns success and exposes the response content in the run output

#### Scenario: Model requests a tool call
- **WHEN** the model response includes a tool call
- **THEN** the runtime executes the tool via `ToolRuntime`, appends the result to the message history, and continues

### Requirement: Minimal stdin/stdout chat example
The system SHALL provide a minimal stdin/stdout example that wires the OpenAI adapter, base prompt store, and local command tool into an agent to perform basic dialogue.

#### Scenario: User enters a prompt
- **WHEN** a user types a line into stdin
- **THEN** the example prints the model response to stdout
