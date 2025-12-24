## ADDED Requirements
### Requirement: File-backed event log
The system SHALL provide a file-backed event log that appends events in order and maintains a verifiable hash chain.

#### Scenario: Verify hash chain
- **WHEN** multiple events are appended to the event log
- **THEN** verify_chain returns true for the stored sequence

### Requirement: File-backed checkpoint
The system SHALL provide a file-backed checkpoint that persists runtime state and allows loading by checkpoint id.

#### Scenario: Save and load checkpoint
- **WHEN** a runtime state is saved to a checkpoint
- **THEN** loading the checkpoint returns the same state and milestone id
