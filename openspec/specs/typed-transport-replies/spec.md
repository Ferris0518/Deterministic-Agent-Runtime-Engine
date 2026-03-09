# typed-transport-replies Specification

## Purpose
Define the canonical transport reply contract so request and reply envelopes use the same typed payload families without envelope-level subtype aliases.

## Requirements

### Requirement: Transport replies use typed payload families
The transport layer SHALL return reply envelopes using the same typed payload families as requests, without relying on `event_type` or weakly-typed dictionary wrappers.

- `EnvelopeKind.MESSAGE` replies MUST carry `MessagePayload`.
- `EnvelopeKind.ACTION` replies MUST carry `ActionPayload`.
- `EnvelopeKind.CONTROL` replies MUST carry `ControlPayload`.
- `EnvelopeKind.SELECT` replies MUST carry `SelectPayload`.

#### Scenario: Agent message request returns assistant message payload
- **WHEN** an agent finishes handling a `TransportEnvelope(kind="message", payload=<MessagePayload>)`
- **THEN** the reply envelope uses `kind="message"`
- **AND** the reply payload is one `MessagePayload` representing the assistant-visible result

#### Scenario: Action request returns typed action payload
- **WHEN** the runtime completes one `TransportEnvelope(kind="action", payload=<ActionPayload>)`
- **THEN** the reply envelope uses `kind="action"`
- **AND** the reply payload is one `ActionPayload` containing `ok/result/code/reason`

#### Scenario: Control request returns typed control payload
- **WHEN** the runtime completes one `TransportEnvelope(kind="control", payload=<ControlPayload>)`
- **THEN** the reply envelope uses `kind="control"`
- **AND** the reply payload is one `ControlPayload` containing `ok/result/code/reason`
