## MODIFIED Requirements

### Requirement: Transport envelope is content-agnostic and distinct from context messages
The system SHALL define a `TransportEnvelope` type that remains distinct from `context.Message` while carrying typed payload families rather than ad-hoc arbitrary payloads.

- The envelope MUST provide a primary strong-typed `kind` categorization that distinguishes `message|select|action|control`.
- The envelope MUST carry a typed payload family selected by `kind`.
- For `kind="action"`, the payload MUST carry a deterministic `resource_action` request.
- For `kind="control"`, the payload MUST carry a deterministic runtime control id from `AgentControl` (e.g. `interrupt|pause|retry|reverse`).
- The envelope model MUST NOT require a second routing subtype field in addition to `kind` in order to route inbound envelopes.

#### Scenario: Envelope carries a control interrupt
- **WHEN** a client sends a `TransportEnvelope` with `kind="control"` and a payload whose `control_id="interrupt"`
- **THEN** the channel can route it to control handling without relying on prompt parsing

### Requirement: Envelope kind supports message, select, action, and control categories
The transport envelope model SHALL provide a primary categorization field for inbound/outbound envelopes that can distinguish:
- `message` (canonical message payloads)
- `select` (approval/choice/form interactions)
- `action` (deterministic resource actions)
- `control` (interrupt/pause/retry/reverse)

The envelope model MUST NOT require a separate subtype field in order to route inbound envelopes.

#### Scenario: Select envelope is distinguishable without prompt parsing
- **GIVEN** a client sends `TransportEnvelope(kind="select", payload=<SelectPayload>)`
- **WHEN** the channel receives it
- **THEN** the channel can route the request deterministically without inspecting prompt text

### Requirement: Agent loop consumes prompt messages only
The runtime integration with `AgentChannel.poll()` SHALL treat polled envelopes as prompt message workload only.

- Agent execution loop MUST NOT be responsible for routing `select`, `action`, or `control`.
- For `kind="message"`, the agent loop MUST only accept typed `MessagePayload` that can normalize to canonical `Message`.
- Any non-message envelope reaching the agent loop MUST be treated as routing error.

#### Scenario: Non-message envelope is rejected in agent loop
- **GIVEN** a non-message envelope is observed in the agent loop
- **WHEN** runtime validation executes
- **THEN** runtime returns an error response
- **AND** does not invoke prompt execution

### Requirement: Entry adapters provide deterministic envelope kinds
Client entry adapters SHALL normalize input into explicit envelope kinds and typed payloads before transport routing.

- `stdio` adapters MAY map slash commands to structured `ACTION/CONTROL/SELECT` envelopes.
- `websocket` and `A2A` adapters MUST send explicit `kind` and typed `payload`.
- Entry adapters MUST NOT rely on transport runtime parsing free-form prompt text to infer action/control/select semantics.

#### Scenario: Websocket sends explicit action envelope
- **GIVEN** a websocket client wants tool introspection
- **WHEN** it sends `kind="action"` with an `ActionPayload` that targets `tools:list`
- **THEN** channel routes the request through action path without text parsing

## ADDED Requirements

### Requirement: Select envelopes carry approval and choice interactions
The transport channel SHALL support `kind="select"` for deterministic selection interactions.

- `SelectPayload` MUST support `select_kind="ask|answered"`.
- `SelectPayload` MUST support `select_domain="approval|choice|form"`.
- Approval interactions MUST use `kind="select"` rather than message event aliases.

#### Scenario: Approval pending is emitted as select ask
- **GIVEN** a tool invocation requires human approval
- **WHEN** the runtime emits the interaction to the client
- **THEN** it sends `TransportEnvelope(kind="select")`
- **AND** the payload uses `select_domain="approval"` and `select_kind="ask"`
