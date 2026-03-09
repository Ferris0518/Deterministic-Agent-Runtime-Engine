## MODIFIED Requirements

### Requirement: Agent loop consumes prompt messages only
The runtime integration with `AgentChannel.poll()` SHALL normalize inbound `MessagePayload` into canonical `Message` before invoking agent execution.

- The transport loop MUST NOT flatten `MessagePayload` into plain text.
- `text`, `attachments`, and `data` from `MessagePayload` MUST be preserved in the canonical `Message` passed into agent execution.

#### Scenario: Polled composite chat message reaches agent intact
- **GIVEN** `AgentChannel.poll()` returns `TransportEnvelope(kind="message", payload=<MessagePayload message_kind="chat" text="look" attachments=[image]>)`
- **WHEN** the base agent transport loop executes that input
- **THEN** the concrete agent receives a canonical `Message`
- **AND** the message still contains the image attachment reference
