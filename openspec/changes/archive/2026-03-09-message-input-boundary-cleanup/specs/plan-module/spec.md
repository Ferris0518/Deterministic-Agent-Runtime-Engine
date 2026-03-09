## MODIFIED Requirements

### Requirement: Task carries orchestration description separately from canonical input
The planning module SHALL allow `Task` to retain orchestration metadata without becoming the sole carrier of user prompt semantics.

- `Task` MUST expose `input_message: Message | None`.
- `Task.description` remains available for plan/milestone descriptions.
- `Task.to_milestones()` SHOULD prefer `input_message.text` for `Milestone.user_input` when present.

#### Scenario: Milestone user input follows canonical task message
- **GIVEN** a `Task` with `description="refactor auth"` and `input_message.text="please refactor auth and review these screenshots"`
- **WHEN** default milestones are derived
- **THEN** the milestone description remains `"refactor auth"`
- **AND** `Milestone.user_input` uses the canonical message text
