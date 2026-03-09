## 1. Transport typed payload baseline

- [x] 1.1 Replace `TransportEnvelope.payload: Any + event_type` with typed payload families in `dare_framework/transport/types.py`
- [x] 1.2 Keep `EnvelopeKind = message/select/action/control` and route inbound envelopes by payload family in transport channel code
- [x] 1.3 Move approval pending/resolved semantics from message event aliases into `SelectPayload(select_kind=ask|answered, select_domain=approval)`
- [x] 1.4 Update transport payload builders, dispatcher contracts, and transport-facing tests to validate typed payload parsing and reply correlation

## 2. Canonical message upgrade

- [x] 2.1 Upgrade `dare_framework/context/types.py::Message` to `kind + text + attachments + data` and add `AttachmentRef`
- [x] 2.2 Update context assemble/STM/query logic to consume canonical `Message` instead of `content: str`
- [x] 2.3 Replace task-description-as-message usage so agent/runtime input paths construct canonical messages directly
- [x] 2.4 Update session/checkpoint/memory persistence code to serialize and restore the upgraded `Message`

## 3. Model adapter serialization

- [x] 3.1 Update `ModelInput` consumers so adapters serialize canonical `Message` instead of plain text content
- [x] 3.2 Implement `chat(text + image attachments[])` serialization for supported adapters and deterministic fallback hooks for unsupported history
- [x] 3.3 Move `tool_call/tool_result` structured semantics from ad-hoc metadata parsing to canonical `Message.data`
- [x] 3.4 Update adapter unit tests to cover chat rich-media messages and structured tool message serialization

## 4. Contract and regression verification

- [x] 4.1 Update transport contract tests that currently assert `payload=str` and `event_type`
- [x] 4.2 Update context/model/integration tests that currently assert `Message.content`
- [x] 4.3 Add golden-path tests for one chat message containing text plus multiple image attachments
- [x] 4.4 Add error-path tests for invalid typed payloads and unsupported attachment/message-kind combinations
