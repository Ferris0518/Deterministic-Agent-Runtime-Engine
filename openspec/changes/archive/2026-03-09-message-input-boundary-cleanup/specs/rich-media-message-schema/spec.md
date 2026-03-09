## MODIFIED Requirements

### Requirement: Canonical message schema supports text, attachments, and structured data
The framework SHALL preserve canonical `Message` semantics at the runtime input boundary instead of flattening top-level input to raw text.

- Top-level agent execution MUST accept canonical `Message` input directly.
- Direct user-prompt helpers MUST prefer canonical `Message` over `Task.description`.
- `Message.kind="tool_call" | "tool_result"` MUST reject construction without structured `data`.

#### Scenario: Direct execution keeps a composite user message intact
- **WHEN** a caller invokes an agent with `Message(kind="chat", text=<text>, attachments=[image...])`
- **THEN** the runtime uses that canonical message as the first user turn
- **AND** `attachments` remain available to context assembly and model serialization
