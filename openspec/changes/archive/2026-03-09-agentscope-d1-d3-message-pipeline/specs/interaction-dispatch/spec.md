## ADDED Requirements

### Requirement: Select dispatch is isolated from action, control, and prompt execution
The system SHALL provide a deterministic dispatch path for `select` envelopes that is separate from prompt execution, action dispatch, and runtime control handling.

- `select` dispatch MUST NOT enter the LLM prompt execution path.
- `select` dispatch MUST NOT be routed through `ActionHandlerDispatcher`.
- `select` dispatch MUST preserve `reply_to` correlation semantics for answered selections.

#### Scenario: Select answer does not execute as a prompt
- **GIVEN** an inbound `TransportEnvelope(kind="select")`
- **WHEN** the interaction layer processes the envelope
- **THEN** it does not invoke the LLM-driven agent execution path
- **AND** it does not route the envelope through `ActionHandlerDispatcher`

### Requirement: Approval interactions use select ask and answered semantics
The deterministic interaction layer SHALL represent approval interactions as `select` payloads.

- Pending approval MUST use `SelectPayload(select_domain="approval", select_kind="ask")`.
- Resolved approval MUST use `SelectPayload(select_domain="approval", select_kind="answered")`.
- The runtime MUST NOT rely on message event aliases such as `approval.pending` or `approval.resolved` as the primary approval contract.

#### Scenario: Approval resolution replies to the pending request
- **GIVEN** an approval request was emitted as `kind="select"` with `select_kind="ask"`
- **WHEN** the user resolves the approval
- **THEN** the resolution is expressed as `kind="select"` with `select_kind="answered"`
- **AND** the reply references the originating request envelope when available
