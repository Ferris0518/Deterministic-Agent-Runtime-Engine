## ADDED Requirements
### Requirement: OpenAI model adapter via LangChain
The system SHALL provide an `IModelAdapter` implementation backed by `langchain-openai` that generates `ModelResponse` from `Message` inputs.

#### Scenario: Generate a chat response
- **WHEN** `generate(...)` is called with messages and no tool definitions
- **THEN** the adapter returns a `ModelResponse` with response content and no tool calls

#### Scenario: Translate tool calls
- **WHEN** the OpenAI model returns one or more tool calls
- **THEN** the adapter returns a `ModelResponse` containing tool call names and arguments in the framework format
