## MODIFIED Requirements

### Requirement: Previous session summary handoff
The runtime SHALL keep the session-loop user-turn source distinct from orchestration description text.

- `Task` MAY carry `input_message: Message`.
- Session initialization MUST prefer `Task.input_message` over synthesizing a user message from `Task.description`.

#### Scenario: Session loop uses canonical task input message
- **GIVEN** a `Task` whose `description` is orchestration text and whose `input_message` is `Message(kind="chat", text=<text>, attachments=[image])`
- **WHEN** the session loop initializes
- **THEN** STM receives `Task.input_message` as the first user turn
- **AND** the runtime does not replace it with a plain-text message from `description`
