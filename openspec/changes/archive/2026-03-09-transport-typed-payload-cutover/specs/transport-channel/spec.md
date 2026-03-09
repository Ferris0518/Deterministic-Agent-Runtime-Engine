## MODIFIED Requirements

### Requirement: AgentChannel rejects unsupported inbound envelope payloads deterministically
The runtime SHALL validate inbound transport envelopes at the channel boundary and reject unsupported payload families with deterministic error semantics before they reach agent execution.

- `EnvelopeKind.MESSAGE` MUST accept only `MessagePayload`.
- `EnvelopeKind.ACTION` MUST accept only `ActionPayload`.
- `EnvelopeKind.CONTROL` MUST accept only `ControlPayload`.
- `EnvelopeKind.SELECT` MUST accept only `SelectPayload`.
- The runtime MUST NOT accept legacy raw `str` or weakly-typed `dict` payloads as transport request payloads.

#### Scenario: Message envelope with invalid payload is rejected before execution
- **WHEN** the runtime receives `TransportEnvelope(kind="message")` whose payload is not a `MessagePayload`
- **THEN** the envelope is rejected before agent execution begins
- **AND** the requester receives a deterministic typed error reply

#### Scenario: Action envelope with invalid payload is rejected before dispatch
- **WHEN** the runtime receives `TransportEnvelope(kind="action")` whose payload is not an `ActionPayload`
- **THEN** the dispatcher is not invoked
- **AND** the requester receives a deterministic typed error reply
