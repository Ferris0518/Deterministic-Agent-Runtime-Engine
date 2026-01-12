## ADDED Requirements
### Requirement: Base system prompt via prompt store
The system SHALL provide a default English base system prompt through the default `IPromptStore` implementation under a stable name (e.g., `base.system`) and expose it to context assembly.

#### Scenario: Default prompt retrieval
- **WHEN** the runtime requests the base system prompt without specifying a version
- **THEN** the prompt store returns the default English system prompt content

#### Scenario: Context assembly uses the base prompt
- **WHEN** an assembled context is built for a milestone
- **THEN** the first message in the assembled context is the base system prompt
