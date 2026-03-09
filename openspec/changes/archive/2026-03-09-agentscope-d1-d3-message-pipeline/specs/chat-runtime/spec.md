## MODIFIED Requirements

### Requirement: LLM-driven execute loop
The runtime SHALL invoke the configured `IModelAdapter` during the execute loop, provide the assembled canonical message history and available tool definitions, and iterate over tool calls until the model returns a final response.

- `Context.assemble()` MUST produce canonical `Message` objects rather than plain text-only entries.
- `IModelAdapter` MUST serialize canonical `Message` into provider-native request messages internally.
- The execute loop MUST append tool calls and tool results back into canonical message history before continuing.

#### Scenario: Model returns a final response
- **WHEN** the model response contains no tool calls
- **THEN** the execute loop returns success and exposes the response content in the run output

#### Scenario: Model requests a tool call
- **WHEN** the model response includes a tool call
- **THEN** the runtime executes the tool via `ToolRuntime`, appends the result to the canonical message history, and continues

### Requirement: Retrieval query derives from current user intent
The default assembly strategy SHALL derive retrieval query from the latest user-intent message in STM.

For `Message(kind="chat")`, retrieval query derivation MUST use the latest non-empty `text` field rather than transport envelope content.

#### Scenario: Latest user chat text drives retrieval query
- **GIVEN** STM contains multiple turns including a latest user `Message(kind="chat")` with text
- **WHEN** `Context.assemble()` is called
- **THEN** LTM and Knowledge retrieval are invoked with that latest user text as query

## ADDED Requirements

### Requirement: Chat messages support text and image attachments in one turn
The runtime SHALL support a single chat message that contains both text and multiple image attachments.

- `Message(kind="chat")` MUST allow non-empty `text` together with one or more image attachment references.
- The assembled message history MUST preserve the association as one logical user turn.
- Model adapters MAY degrade unsupported image history, but the canonical chat message structure MUST remain intact before adapter-specific conversion.

#### Scenario: User sends one text and multiple images
- **WHEN** the runtime receives one user chat message with text and two image attachments
- **THEN** the message history contains one canonical `Message(kind="chat")`
- **AND** both image attachments remain associated with that same user turn
