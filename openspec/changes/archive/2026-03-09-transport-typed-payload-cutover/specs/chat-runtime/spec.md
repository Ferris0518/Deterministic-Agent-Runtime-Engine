## MODIFIED Requirements

### Requirement: LLM-driven execute loop
The runtime SHALL invoke the configured `IModelAdapter` during the execute loop, provide the assembled canonical message history and available tool definitions, and iterate over tool calls until the model returns a final response.

- `Context.assemble()` MUST produce canonical `Message` objects rather than plain text-only entries.
- `IModelAdapter` MUST serialize canonical `Message` into provider-native request messages internally.
- The execute loop MUST append tool calls and tool results back into canonical message history before continuing.
- The transport-driven execute loop MUST return typed reply envelopes without using transport `event_type`.

#### Scenario: Model returns a final response
- **WHEN** the model response contains no tool calls
- **THEN** the execute loop returns success and exposes the response content in the run output
- **AND** the transport reply is `EnvelopeKind.MESSAGE` carrying one assistant `MessagePayload`

#### Scenario: Model requests a tool call
- **WHEN** the model response includes a tool call
- **THEN** the runtime executes the tool via `ToolRuntime`, appends the result to the canonical message history, and continues
- **AND** transport intermediate events are emitted as typed message payloads instead of `event_type` aliases
