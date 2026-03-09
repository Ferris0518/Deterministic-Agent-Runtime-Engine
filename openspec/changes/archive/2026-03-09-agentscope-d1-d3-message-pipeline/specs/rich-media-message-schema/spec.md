## ADDED Requirements

### Requirement: Canonical message schema supports text, attachments, and structured data
The system SHALL define a canonical framework `Message` schema that is independent from provider-native message formats and can represent chat text, image attachments, and structured tool-related data.

- `Message` MUST remain the single canonical message type inside the framework runtime.
- `Message` MUST expose `id`, `role`, `kind`, `text`, `attachments`, `data`, `name`, `metadata`, and `mark`.
- `Message.role` MUST use a deterministic finite type rather than unconstrained strings.
- `Message.kind` MUST distinguish at least `chat`, `thinking`, `tool_call`, `tool_result`, and `summary`.
- `Message.kind` SHOULD be represented by a deterministic finite type rather than unconstrained strings.
- `Message.attachments` MUST support image attachment references via a typed `AttachmentRef` structure rather than raw dictionaries.
- `Message.data` MUST be available for structured message kinds such as `tool_call` and `tool_result`.
- `Message.kind="thinking" | "summary" | "tool_call"` MUST reject attachments at schema validation time.
- `Message.data` MUST be the primary structured source for `tool_call/tool_result`; `metadata` MUST NOT be required as a semantic fallback.

#### Scenario: Chat message carries text and multiple images
- **WHEN** a user message is represented as `Message(kind="chat")` with non-empty `text` and multiple image attachments
- **THEN** the runtime preserves both the text and all attachment references in a single canonical message

### Requirement: Message payload normalizes losslessly into canonical message
The system SHALL define a `MessagePayload` transport contract that can be losslessly normalized into canonical `Message`.

- `MessagePayload` MUST include `id`, `metadata`, `role`, `message_kind`, `text`, `attachments`, and `data`.
- `MessagePayload.role` and `MessagePayload.message_kind` SHOULD use deterministic finite types rather than unconstrained strings.
- `MessagePayload.message_kind` MUST map deterministically to `Message.kind`.
- For `message_kind="chat"`, the payload MUST support `text + attachments` without requiring a separate chat-specific body type.
- `MessagePayload` MUST reject unsupported attachment/message-kind combinations during payload validation.

#### Scenario: Message payload becomes canonical message
- **WHEN** the runtime receives `TransportEnvelope(kind="message", payload=<MessagePayload>)`
- **THEN** the payload is normalized into one canonical `Message`
- **AND** no message semantics are taken from transport-only fields
